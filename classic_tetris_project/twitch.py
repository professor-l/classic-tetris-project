import irc.client
import irc.events
import logging
import re
import requests
import time
from urllib.parse import quote
from django.core.cache import cache
from threading import Thread
from typing import Callable

from .env import env

TWITCH_API = "https://api.twitch.tv/helix"
TWITCH_OAUTH_API = "https://id.twitch.tv/oauth2"
TWITCH_MESSAGING_API = "https://tmi.twitch.tv"
TWITCH_SERVER = "irc.chat.twitch.tv"
TWITCH_PORT = 6667

logger = logging.getLogger("twitch-bot")

class APIClient:
    def __init__(self, client_id, client_secret, client_auth_code, client_redirect_uri):
        self.client_id = client_id
        self.token_manager = TokenManager(client_id, client_secret, client_auth_code, client_redirect_uri)

    def default_headers(self):
        token = self.token_manager.get_app_access_token()
        return {
            "Client-ID": self.client_id,
            "Authorization": f"Bearer {token}"
        }

    def _request(self, endpoint, params={}, headers={}, api=TWITCH_API):
        headers = { **self.default_headers(), **headers }
        response = requests.get(f"{api}/{endpoint}", params=params, headers=headers)
        return response.json()

    def user(self, client=None, **user_params):
        params = {}

        if ("login" in user_params):
            params["login"] = user_params["login"]
        if ("id" in user_params):
            params["id"] = user_params["id"]

        response = self._request("users", params)

        if "error" in response:
            return None
        elif response["data"]:
            user_obj = response["data"][0]
            return self.wrap_user_dict(user_obj, client)

    def user_from_username(self, username=None, client=None):
        return self.user(client, login=username)

    def user_from_id(self, user_id, client=None):
        return self.user(client, id=user_id)

    def own_user(self, token, client=None):
        response = self._request("users", headers={ "Authorization": f"Bearer {token}" })
        if "error" in response:
            return None
        elif response["data"]:
            user_obj = response["data"][0]
            return self.wrap_user_dict(user_obj, client)

    def usernames_in_channel(self, channel):
        channel_user = self.user_from_username(username=channel)
        channel_id = channel_user.id
        bot_user = self.user_from_username(username=env("TWITCH_USERNAME", default=""))
        bot_id = bot_user.id

        params = {
            "broadcaster_id": channel_id,
            "moderator_id": bot_id,
            "first": 1000
        }
        headers = {
            "Client-ID": self.client_id,
            "Authorization": f'Bearer {env("TWITCH_TOKEN")}'
        }

        users = []
        while True:
            response = self._request("chat/chatters", params=params, headers=headers)
            if "error" in response:
                return None

            logins = [entry["user_login"] for entry in response["data"]]
            users.extend(logins)
            if not response["pagination"]:
                break

            params.after = response["pagination"]["cursor"]

        return users

    def wrap_user_dict(self, user_dict, client=None):
        return User(
            client=client,
            username=user_dict["login"],
            id=user_dict["id"],
            display_name=user_dict["display_name"],
            tags=user_dict
        )


# Fetches, stores, and renews an app access token as described in
# https://dev.twitch.tv/docs/authentication/getting-tokens-oauth#oauth-client-credentials-flow

# TODO Much of this can probably be done through authlib:
# https://docs.authlib.org/en/latest/client/frameworks.html#accessing-oauth-resources
class TokenManager:
    # Get a new token 24 hours before the current one expires
    EXPIRATION_BUFFER = 24 * 60 * 60

    def __init__(self, client_id, client_secret, client_auth_code, client_redirect_uri):
        self.client_id = client_id
        self.client_secret = client_secret
        self.client_auth_code = client_auth_code
        self.client_redirect_uri = client_redirect_uri

    def get_app_access_token(self):
        token = cache.get("twitch.oauth.app_access_token")
        if token:
            return token
        else:
            return self.create_app_access_token()

    def create_app_access_token(self):
        response = requests.post(f"{TWITCH_OAUTH_API}/token", params={
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "grant_type": "client_credentials",
        })
        data = response.json()
        if "access_token" not in data:
            raise Exception(str(data["message"]) or "app access oauth failed")

        token = data["access_token"]
        expires_in = int(data["expires_in"])
        self.store_app_access_token(token, expires_in)
        return token

    def store_app_access_token(self, token, expires_in):
        cache.set("twitch.oauth.app_access_token", token, timeout=expires_in - TokenManager.EXPIRATION_BUFFER)

    def get_or_refresh_user_access_token(self):
        access_token = cache.get("twitch.oauth.user_access_token")
        if access_token:
            return access_token
        refresh_token = cache.get("twitch.oauth.user_refresh_token")
        if refresh_token:
            return self.refresh_user_access_token(refresh_token)
        else:
            return self.get_user_access_token()

    def get_user_access_token(self):
        response = requests.post(f"{TWITCH_OAUTH_API}/token", params={
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "code": self.client_auth_code,
            "grant_type": "authorization_code",
            "redirect_uri": self.client_redirect_uri,
        })
        data = response.json()
        if "access_token" not in data:
            if "message" in data:
                logger.error(data["message"])
            self.raise_auth_code_exception()

        access_token = data["access_token"]
        expires_in = int(data["expires_in"])
        refresh_token = data["refresh_token"]
        self.store_user_access_token(access_token, expires_in, refresh_token)
        return access_token

    def raise_auth_code_exception(self):
        auth_code_url = f"{TWITCH_OAUTH_API}/authorize?client_id={self.client_id}&redirect_uri={self.client_redirect_uri}&response_type=code&scope=chat:read%20chat:edit%20moderator:read:chatters"
        raise Exception(f"User oauth failed. Go to {auth_code_url} for a new TWITCH_AUTH_CODE")

    def refresh_user_access_token(self, refresh_token):
        response = requests.post(f"{TWITCH_OAUTH_API}/token", params={
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "grant_type": "refresh_token",
            "refresh_token": quote(refresh_token),
        })
        data = response.json()
        if "access_token" not in data:
            if "message" in data:
                logger.error(data["message"])
            self.raise_auth_code_exception()

        access_token = data["access_token"]
        expires_in = int(data["expires_in"])
        refresh_token = data["refresh_token"]
        self.store_user_access_token(access_token, expires_in, refresh_token)
        return access_token

    def store_user_access_token(self, access_token, expires_in, refresh_token):
        cache.set("twitch.oauth.user_access_token", access_token, timeout=expires_in)
        cache.set("twitch.oauth.user_refresh_token", refresh_token, timeout=None)

# IRC client wrapper for interacting with Twitch chat
class IrcClient:
    def __init__(self, username, token_manager, default_channels=[]):
        # type: (str, TokenManager, list[str]) -> None
        self.username = username
        self.token_manager = token_manager
        self.default_channels = default_channels
        self.reactor = irc.client.Reactor()
        self.connection = self.reactor.server()
        for event in irc.events.all:
            if event != 'pubmsg':
                self.on_event(event, lambda c, e : logger.info(f"{e.type.upper()}: {e.arguments}"))

        self.on_event("welcome", self.handle_welcome)
        self.on_event("reconnect", self.handle_reconnect)
        self.on_event("disconnect", self.handle_disconnect)

    def handle_welcome(self, c, e):
        # type: (irc.client.ServerConnection, irc.client.Event) -> None
        self.connection.cap("REQ", ":twitch.tv/tags")
        self.connection.cap("REQ", ":twitch.tv/commands")

        Thread(target=self.join_channels).start()

    def start(self):
        self.user_obj = API.user_from_username(self.username, self)
        self.user_id = self.user_obj.id

        token = f'oauth:{self.token_manager.get_or_refresh_user_access_token()}'
        self.connection.connect(TWITCH_SERVER, TWITCH_PORT, self.username, token)
        self.reactor.process_forever()

    def on_event(self, event, handler):
        # type: (str, Callable[[irc.client.ServerConnection, irc.client.Event], None]) -> None
        self.connection.add_global_handler(event, handler)

    def on_event_decorator(self, event):
        def _add_handler(handler):
            # type: (Callable[[irc.client.ServerConnection, irc.client.Event], None]) -> None
            self.connection.add_global_handler(event, handler)
        return _add_handler

    def handle_disconnect(self, c, e):
        # type: (irc.client.ServerConnection, irc.client.Event) -> None
        if e.arguments and e.arguments[0] == 'Connection reset by peer':
            # assume invalid token
            refresh_token = cache.get("twitch.oauth.user_refresh_token")
            if refresh_token:
                token = f'oauth:{self.token_manager.refresh_user_access_token(refresh_token)}'
            else:
                self.token_manager.raise_auth_code_exception()
            self.connection.connect(TWITCH_SERVER, TWITCH_PORT, self.username, token)

    def handle_reconnect(self, c, e):
        # type: (irc.client.ServerConnection, irc.client.Event) -> None
        timeout = 1
        while True:
            try:
                self.connection.reconnect()
                return
            except irc.client.ServerConnectionError:
                time.sleep(timeout)
                timeout = min(64, timeout * 2)

    def on_message(self, handler):
        self.connection.add_global_handler("pubmsg", lambda c, e: self._handle_message(e, handler))
        self.connection.add_global_handler("whisper", lambda c, e: self._handle_message(e, handler))
        return handler

    def _handle_message(self, event, handler):
        tags = { tag["key"]: tag["value"] for tag in event.tags }
        username = re.match(r"\w+!(\w+)@[\w.]+", event.source)[1]
        author = User(self, username, tags["user-id"], tags["display-name"], tags)
        if event.type == "pubmsg":
            channel = PublicChannel(self, event.target[1:])
        elif event.type == "whisper":
            channel = Whisper(self, author)
        else:
            raise ValueError(f"Unexpected message type {event.type}")
        message = Message(event.arguments[0], author, channel)
        handler(message)

    def send_message(self, target, text):
        self.connection.privmsg(target, text)

    def get_user(self, user_id):
        return API.user_from_id(user_id, self)

    def get_channel(self, channel_name):
        return PublicChannel(self, channel_name)

    def join_channels(self):
        from .models import TwitchChannel
        channel_names = (self.default_channels +
                         list(TwitchChannel.objects.filter(connected=True).values_list("twitch_user__username",
                                                                                       flat=True)))
        for channel in channel_names:
            self.join_channel(channel)
            # Band-aid to prevent Twitch from disconnecting the bot for joining too many channels at
            # once
            time.sleep(0.5)

    def join_channel(self, channel_name):
        logger.info(f"Joining channel #{channel_name}")
        self.connection.join(f"#{channel_name}")

    def leave_channel(self, channel_name):
        logger.info(f"Leaving channel #{channel_name}")
        self.connection.part(f"#{channel_name}")


class User:
    def __init__(self, client, username, id, display_name, tags={}):
        self.client = client
        self.username = username
        self.id = id
        self.display_name = display_name
        self.tags = tags

    @property
    def is_moderator(self):
        return self.tags.get("mod") == "1"

    def send_message(self, message):
        if self.client is None:
            raise Exception("send_message called without client")
        whisper = Whisper(self.client, self)
        whisper.send_message(message)


class Message:
    def __init__(self, content, author, channel):
        self.content = content
        self.author = author
        self.channel = channel


class Channel:
    def __init__(self, client):
        self.client = client

class PublicChannel(Channel):
    type = "channel"
    def __init__(self, client, name):
        super().__init__(client)
        self.name = name

    def send_message(self, message):
        self.client.send_message(f"#{self.name}", message)

class Whisper(Channel):
    type = "whisper"
    def __init__(self, client, author):
        super().__init__(client)
        self.author = author

    def send_message(self, message):
        self.client.send_message("#jtv", f"/w {self.author.username} {message}")



API = APIClient(
    env("TWITCH_CLIENT_ID", default=""),
    env("TWITCH_CLIENT_SECRET", default=""),
    env("TWITCH_AUTH_CODE", default=""),
    env("TWITCH_REDIRECT_URI", default=""),
)

if API.client_id != "":
    client = IrcClient(
        env("TWITCH_USERNAME", default=""),
        API.token_manager,
        default_channels=[env("TWITCH_USERNAME", default="")]
    )
