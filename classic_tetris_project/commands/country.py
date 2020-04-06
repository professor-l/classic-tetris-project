from .command import Command, CommandException
from ..countries import Country

@Command.register("country", "getcountry",
                  usage="country [username] (default username you)")
class GetCountryCommand(Command):
    def execute(self, *username):
        username = username[0] if len(username) == 1 else self.context.args_string
        platform_user = (self.platform_user_from_username(username) if username
                         else self.context.platform_user)
        user = self.context.user

        if platform_user and user.country:
            self.send_message("{user_tag} is from {country}!".format(
                user_tag=platform_user.user_tag,
                country=Country.get_country(user.country).full_name
            ))
        else:
            self.send_message("User has not set a country.")

@Command.register("setcountry",
                  usage="setcountry <three-letter country code>")
class SetCountryCommand(Command):
    def execute(self, country):
        if not self.context.user.set_country(country):
            raise CommandException("Invalid country.")
        else:
            country = Country.get_country(self.context.user.country)
            self.send_message(f"Your country is now {country.full_name}!")
