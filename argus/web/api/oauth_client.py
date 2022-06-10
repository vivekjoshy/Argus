from authlib.integrations.base_client import MismatchingStateError, OAuthError
from authlib.integrations.starlette_client import OAuth
from fastapi import APIRouter
from fastapi_versioning import version
from starlette import status
from starlette.requests import Request
from starlette.responses import RedirectResponse, Response

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


@router.get("/login", tags=["OAuth 2.0"])
@version(1, 0)
async def login(request: Request):
    redirect_uri = request.url_for("callback")
    return await oauth.discord.authorize_redirect(request, redirect_uri)


@router.get("/callback", tags=["OAuth 2.0"])
@version(1, 0)
async def callback(request: Request):
    try:
        token = await oauth.discord.authorize_access_token(request)
        request.session["token"] = token
    except MismatchingStateError:
        return {"Status": "Failed", "Reason": "Token Invalid"}
    except OAuthError:
        return {"Status": "Failed", "Reason": "Access Denied"}
    redirect_url = request.base_url
    return RedirectResponse(redirect_url)


@router.get("/authorized", tags=["OAuth 2.0"])
@version(1, 0)
async def authorized(request: Request, response: Response):
    token = request.session.get("token")
    if token:
        return {"Status": "Success"}
    else:
        response.status_code = status.HTTP_401_UNAUTHORIZED
        return {"Status": "Failed", "Reason": "Session Not Found"}


@router.get("/logout", tags=["OAuth 2.0"])
@version(1, 0)
async def logout(request: Request, response: Response):
    token = request.session.get("token")
    if token:
        request.session.pop("token")
        return {"Status": "Success"}
    else:
        response.status_code = status.HTTP_401_UNAUTHORIZED
        return {"Status": "Failed", "Reason": "Session Not Found"}
