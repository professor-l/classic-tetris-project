from .command import Command, CommandException
from ..countries import Country
from ..util import Platform, DocSection

@Command.register()
class GetCountryCommand(Command):
    """
    Outputs the country of the specified user, or yourself if no argument is
    provided.
    """
    aliases = ("country", "getcountry")
    supported_platforms = (Platform.DISCORD, Platform.TWITCH)
    usage = "country [username] (default username you)"
    section = DocSection.USER

    def execute(self, *username):
        username = username[0] if len(username) == 1 else self.context.args_string
        platform_user = (self.platform_user_from_username(username) if username
                         else self.context.platform_user)
        user = platform_user.user if platform_user else None

        if user and user.country:
            self.send_message("{name} is from {country}!".format(
                name=self.context.display_name(platform_user),
                country=Country.get_country(user.country).full_name
            ))
        else:
            self.send_message("User has not set a country.")

@Command.register()
class SetCountryCommand(Command):
    """
    Sets your country in the database. You can find a list of the three-letter
    codes [here](https://www.iban.com/country-codes) under the "Alpha-3 codes"
    column.
    """
    aliases = ("setcountry",)
    supported_platforms = (Platform.DISCORD, Platform.TWITCH)
    usage = "setcountry <three-letter country code>"
    section = DocSection.USER

    def execute(self, country):
        if not self.context.user.set_country(country):
            raise CommandException("Invalid country.")
        else:
            country = Country.get_country(self.context.user.country)
            self.send_message(f"Your country is now {country.full_name}!")
