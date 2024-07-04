import uuid
from authlib.integrations.django_client import OAuth
from django.core.cache import cache

from ..env import env

oauth = OAuth()
oauth.register(
    name="discord",
    client_id=env("DISCORD_CLIENT_ID"),
    client_secret=env("DISCORD_CLIENT_SECRET"),
    access_token_url="https://discordapp.com/api/oauth2/token",
    authorize_url="https://discordapp.com/api/oauth2/authorize",
    api_base_url="https://discordapp.com/api/v6/",
    client_kwargs={"scope": "identify"}
)
oauth.register(
    name="twitch",
    client_id=env("TWITCH_CLIENT_ID"),
    client_secret=env("TWITCH_CLIENT_SECRET"),
    access_token_url="https://id.twitch.tv/oauth2/token",
    authorize_params={"force_verify": "true"},
    authorize_url="https://id.twitch.tv/oauth2/authorize",
    access_token_params={"client_id": env("TWITCH_CLIENT_ID"),
                         "client_secret": env("TWITCH_CLIENT_SECRET")},
    client_kwargs={"scope": ""}
)

discord = oauth.discord
twitch = oauth.twitch

class State:
    CACHE_TIMEOUT = 12 * 60 * 60 # 12 hours
    ALLOWED_KEYS = ["next", "merge_accounts"]

    def __init__(self, params={}, state_id=None):
        self.state_id = state_id or uuid.uuid4().hex
        self.params = { k: v for k, v in params.items() if k in State.ALLOWED_KEYS }

    def __getitem__(self, key):
        return self.params.get(key)

    def store(self):
        cache.set(f"oauth_states.{self.state_id}", self.params, timeout=State.CACHE_TIMEOUT)
        return self.state_id

    def expire(self):
        cache.delete(f"oauth_state.{self.state_id}")

    @staticmethod
    def from_request(request):
        return State(request.GET)

    @staticmethod
    def retrieve(state_id):
        params = cache.get(f"oauth_states.{state_id}")
        if params is None:
            return None
        else:
            return State(params, state_id)
