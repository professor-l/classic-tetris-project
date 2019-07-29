import irc.client
import re
import requests

from .env import env


TWITCH_API = "https://api.twitch.tv/kraken/"
TWITCH_SERVER = "irc.chat.twitch.tv"
TWITCH_PORT = 6667

class APIClient:
    def __init__(self, client_id):
        self.client_id = client_id
        self.headers = {
            "Accept": "application/vnd.twitchtv.v5+json",
            "Client-ID": client_id
        }

    def _request(self, endpoint, params={}):
        response = requests.get(f"{TWITCH_API}{endpoint}", params=params, headers=self.headers)
        return response.json()

    def user_from_username(self, username, client=None):
        response = self._request("users", { "login": username })
        user_list = response["users"]
        if user_list:
            user_obj = user_list[0]
            return User(
                client=client,
                username=user_obj["name"],
                id=user_obj["_id"],
                display_name=user_obj["display_name"],
                tags=user_obj
            )
        else:
            return None

    def user_from_id(self, user_id, client=None):
        user_obj = self._request(f"users/{user_id}")
        return User(
            client=client,
            username=user_obj["name"],
            id=user_obj["_id"],
            display_name=user_obj["display_name"],
            tags=user_obj
        )




class Client:
    def __init__(self, username, token, channels=[]):
        self.username = username
        self.token = token
        self.channels = channels
        self.reactor = irc.client.Reactor()
        self.connection = self.reactor.server()

        self.connection.add_global_handler("welcome", self.on_welcome)

    def on_welcome(self, c, e):
        c.cap("REQ", ":twitch.tv/tags")
        c.cap("REQ", ":twitch.tv/commands")
        for channel in self.channels:
            c.join(f"#{channel}")

    def start(self):
        self.connection.connect(TWITCH_SERVER, TWITCH_PORT, self.username, self.token)
        self.reactor.process_forever()

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
        message = Message(event.arguments[0], author, channel)
        handler(message)

    def send_message(self, target, text):
        self.connection.privmsg(target, text)

    def get_user(self, user_id):
        return API.user_from_id(user_id, self)



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
    def __init__(self, client, name):
        super().__init__(client)
        self.name = name

    def send_message(self, message):
        self.client.send_message(f"#{self.name}", message)

class Whisper(Channel):
    def __init__(self, client, author):
        super().__init__(client)
        self.author = author

    def send_message(self, message):
        self.client.send_message("#jtv", f"/w {self.author.username} {message}")



API = APIClient(env("TWITCH_CLIENT_ID"))

client = Client(
    env("TWITCH_USERNAME"),
    env("TWITCH_TOKEN"),
    channels=["classictetrisbottest"]
)
