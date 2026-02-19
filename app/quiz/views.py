from aiohttp import web
from aiohttp_apispec import querystring_schema, request_schema, response_schema

from app.quiz.schemes import (
    ListQuestionSchema,
    QuestionSchema,
    ThemeIdSchema,
    ThemeListSchema,
    ThemeSchema,
)
from app.web.app import View
from app.web.mixins import AuthRequiredMixin
from app.web.utils import json_response


class ThemeAddView(AuthRequiredMixin, View):
    @request_schema(ThemeSchema)
    @response_schema(ThemeSchema)
    async def post(self):
        data = self.request["data"]
        title = data["title"]
        
        # Check if theme already exists
        existing_theme = await self.store.quizzes.get_theme_by_title(title)
        if existing_theme:
            raise web.HTTPConflict(text="Theme already exists")
        
        theme = await self.store.quizzes.create_theme(title)
        return json_response({"id": theme.id, "title": theme.title})


class ThemeListView(AuthRequiredMixin, View):
    @response_schema(ThemeListSchema)
    async def get(self):
        themes = await self.store.quizzes.list_themes()
        return json_response({"themes": [{"id": theme.id, "title": theme.title} for theme in themes]})


class QuestionAddView(AuthRequiredMixin, View):
    @request_schema(QuestionSchema)
    @response_schema(QuestionSchema)
    async def post(self):
        data = self.request["data"]
        title = data["title"]
        theme_id = data["theme_id"]
        answers_data = data["answers"]
        
        # Validate theme exists
        theme = await self.store.quizzes.get_theme_by_id(theme_id)
        if not theme:
            raise web.HTTPNotFound(text="Theme not found")
        
        # Check if question already exists
        existing_question = await self.store.quizzes.get_question_by_title(title)
        if existing_question:
            raise web.HTTPConflict(text="Question already exists")
        
        # Validate answers
        if len(answers_data) < 2:
            raise web.HTTPBadRequest(text="Question must have at least 2 answers")
        
        correct_answers = [a for a in answers_data if a.get("is_correct", False)]
        if len(correct_answers) != 1:
            raise web.HTTPBadRequest(text="Question must have exactly 1 correct answer")
        
        # Create answer models
        from app.quiz.models import AnswerModel
        answers = [AnswerModel(title=a["title"], is_correct=a["is_correct"]) for a in answers_data]
        
        question = await self.store.quizzes.create_question(title, theme_id, answers)
        
        return json_response({
            "id": question.id,
            "title": question.title,
            "theme_id": question.theme_id,
            "answers": [{"title": a.title, "is_correct": a.is_correct} for a in question.answers]
        })


class QuestionListView(AuthRequiredMixin, View):
    @querystring_schema(ThemeIdSchema)
    @response_schema(ListQuestionSchema)
    async def get(self):
        theme_id = self.request.get("theme_id")
        
        questions = await self.store.quizzes.list_questions(theme_id)
        
        result = []
        for question in questions:
            question_data = {
                "id": question.id,
                "title": question.title,
                "theme_id": question.theme_id,
                "answers": [
                    {"title": answer.title, "is_correct": answer.is_correct}
                    for answer in question.answers
                ]
            }
            result.append(question_data)
        
        return json_response({"questions": result})
