from hashlib import sha256

from aiohttp import web
from aiohttp_apispec import request_schema, response_schema

from app.admin.schemes import AdminSchema
from app.web.app import View
from app.web.mixins import AuthRequiredMixin
from app.web.utils import json_response


class AdminLoginView(View):
    @request_schema(AdminSchema)
    @response_schema(AdminSchema, 200)
    async def post(self):
        data = self.request["data"]
        email = data["email"]
        password = data["password"]
        
        admin = await self.store.admins.get_by_email(email)
        if not admin:
            raise web.HTTPForbidden(text="Invalid credentials")
        
        hashed_password = sha256(password.encode()).hexdigest()
        if admin.password != hashed_password:
            raise web.HTTPForbidden(text="Invalid credentials")
        
        # Store admin in session
        from aiohttp_session import get_session
        session = await get_session(self.request)
        session["admin"] = {"id": admin.id, "email": admin.email}
        
        return json_response({"id": admin.id, "email": admin.email})


class AdminCurrentView(AuthRequiredMixin, View):
    @response_schema(AdminSchema, 200)
    async def get(self):
        return json_response({"id": self.request.admin.id, "email": self.request.admin.email})
