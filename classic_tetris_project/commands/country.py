from .command import Command, CommandException
from ..countries import countries

@Command.register("country", "getcountry",
                  usage="country [username] (default username you)")
class GetCountryCommand(Command):
    def execute(self, *username):
        username = username[0] if len(username) == 1 else self.context.args_string
        platform_user = (self.platform_user_from_username(username) if username
                         else self.context.platform_user)

        if platform_user and platform_user.user.country:
            self.send_message("{user_tag} is from {country}!".format(
                user_tag=platform_user.user_tag,
                country=countries[platform_user.user.country]
            ))
        else:
            self.send_message("User has not set a country.")

@Command.register("setcountry",
                  usage="setcountry <three-letter country code>")
class SetCountryCommand(Command):
    def execute(self, country):
        if not self.context.user.set_country(country):
            raise CommandException("Invalid country code. See "
                "https://www.iban.com/country-codes to find your 3-digit "
                "country code.")
        else:
            self.send_message(f"Your country is now {countries[country.upper()]}!")
