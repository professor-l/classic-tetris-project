from authlib.integrations.django_client import OAuth

from ..env import env

oauth = OAuth()
oauth.register(
    name="discord",
    client_id=env("DISCORD_CLIENT_ID"),
    client_secret=env("DISCORD_CLIENT_SECRET"),
    authorize_url="https://discordapp.com/api/oauth2/authorize",
    access_token_url="https://discordapp.com/api/oauth2/token",
    api_base_url="https://discordapp.com/api/v6",
    client_kwargs={"scope": "identify"}
)

discord = oauth.discord
