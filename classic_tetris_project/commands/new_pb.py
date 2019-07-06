from .command import Command, ArgException, register_command

@register_command("newpb", "setpb")
class SetPBCommand(Command):
    pass