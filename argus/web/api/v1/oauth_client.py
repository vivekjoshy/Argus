from authlib.integrations.starlette_client import OAuth
from fastapi import APIRouter
from starlette.requests import Request

from argus.config import config

router = APIRouter(prefix="/api/v1/auth")

oauth = OAuth()
oauth.register(
    name="discord",
    client_id=config["bot"]["client_id"],
    client_secret=config["bot"]["client_secret"],
    access_token_url="https://discord.com/api/oauth2/token",
    access_token_params=None,
    authorize_url="https://discord.com/api/v10/oauth2/authorize",
    authorize_params=None,
    api_base_url="https://discord.com/api/v10/",
    client_kwargs={"scope": "identify email guilds"},
)


@router.get("/login")
async def login(request: Request):
    redirect_uri = request.url_for("callback")
    return await oauth.discord.authorize_redirect(request, redirect_uri)


@router.get("/callback")
async def callback(request: Request):
    token = await oauth.discord.authorize_access_token(request)
    return dict(token)
