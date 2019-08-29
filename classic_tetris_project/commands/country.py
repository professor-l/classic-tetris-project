from .command import Command, CommandException
from ..util import Platform
from ..countries import countries

@Command.register("country", "getcountry",
                  usage="country [username] (default username you)")
class GetCountryCommand(Command):
    def execute(self, username=None):
        if username is None:
            platform_user = self.context.platform_user
        elif self.context.platform == Platform.DISCORD:
            platform_user = Command.discord_user_from_username(username)
        elif self.context.platform == Platform.TWITCH:
            platform_user = Command.twitch_user_from_username(username)

        if platform_user and platform_user.user.country:
            self.send_message("{user_tag} is from {country}!".format(
                user_tag=platform_user.user_tag,
                country=countries[platform_user.user.country]
            ))
        else:
            self.send_message("User has not set a country.")

@Command.register("setcountry",
                  usage="setpb <three-letter country code>")
class SetCountryCommand(Command):
    def execute(self, country): 
        if not self.context.user.set_country(country):
            raise CommandException("Invalid country code. See "
                "https://www.iban.com/country-codes to find your 3-digit "
                "country code.")
        else:
            self.send_message(f"Your country is now {countries[country.upper()]}!")
