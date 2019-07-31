from .command import Command, CommandException, register_command
from ..countries import countries

@register_command("setcountry")
class SetCountryCommand(Command):
    usage = "setpb <three-letter country code>"

    def execute(self, country): 
        if not self.context.user.set_country(country):
            raise CommandException("Invalid country code. See "
                "https://www.iban.com/country-codes to find your 3-digit "
                "country code.")
        else:
            self.send_message(f"Your country is now {countries[country.upper()]}!")
