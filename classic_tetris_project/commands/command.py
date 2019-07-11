from inspect import signature
from ..util import Platform

class CommandException(Exception):
    def __init__(self, message=None, send_usage=False):
        self.message = message
        self.send_usage = send_usage

class Command:
    def __init__(self, context):
        self.context = context
        self.args = context.args

    @property
    def supported_platforms(self):
        return [Platform.DISCORD, Platform.TWITCH]

    def check_support_and_execute(self):
        if self.context.platform in self.supported_platforms:
            try:
                min_args, max_args = self.arity
                num_args = len(self.args)
                if num_args < min_args or (max_args is not None and num_args > max_args):
                    raise CommandException(send_usage=True)
                else:
                    self.execute(*self.args)
            except CommandException as e:
                if e.message:
                    self.send_message(e.message)
                if e.send_usage:
                    self.send_usage()
            except TypeError as e:
                import ipdb; ipdb.set_trace()
                self.send_usage()
        else:
            self.send_message("Command not supported on this platform.")

    def send_message(self, message):
        self.context.send_message(message)

    def send_usage(self):
        # Add `wrapper` if in Discord
        formatted = self.context.format_code("{prefix}{usage}".format(
            prefix=self.context.PREFIX,
            usage=self.usage
        ))
        self.send_message(f"Usage: {formatted}")

    @property
    def arity(self):
        required = 0
        optional = 0
        sig = signature(self.execute)
        for param in sig.parameters.values():
            if param.kind == param.VAR_POSITIONAL:
                optional = None
            else:
                if param.default == param.empty:
                    required += 1
                if optional is not None:
                    optional += 1
        return required, optional



COMMAND_MAP = {}

def register_command(*aliases):
    def register(command):
        for alias in aliases:
            COMMAND_MAP[alias] = command
        return command
    return register
