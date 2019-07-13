import re
import irc.client

import logging


TWITCH_SERVER = "irc.chat.twitch.tv"
TWITCH_PORT = 6667

class Client:
    def __init__(self, username, token, client_id=None, channels=[]):
        # logging.basicConfig(level=logging.DEBUG)
        self.username = username
        self.token = token
        self.client_id = client_id
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
        author = User(self, username, tags)
        if event.type == "pubmsg":
            channel = PublicChannel(self, event.target[1:])
        elif event.type == "whisper":
            channel = Whisper(self, author)
        message = Message(event.arguments[0], author, channel)
        handler(message)

    def send_message(self, target, text):
        self.connection.privmsg(target, text)



class User:
    def __init__(self, client, username, tags):
        self.username = username
        self.display_name = tags["display-name"]
        self.id = tags["user-id"]
        self.type = tags["user-type"]



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
