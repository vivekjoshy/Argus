from authlib.integrations.base_client import MismatchingStateError
from authlib.integrations.starlette_client import OAuth
from fastapi import APIRouter
from fastapi_versioning import version
from starlette.requests import Request

from argus.config import config

router = APIRouter(prefix="/auth")

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


@router.get("/login", tags=["OAuth Login"])
@version(1, 0)
async def login(request: Request):
    redirect_uri = request.url_for("callback")
    return await oauth.discord.authorize_redirect(request, redirect_uri)


@router.get("/callback", tags=["OAuth Login"])
@version(1, 0)
async def callback(request: Request):
    try:
        token = await oauth.discord.authorize_access_token(request)
    except MismatchingStateError:
        return {"Status": "Failed"}
    return dict(token)
