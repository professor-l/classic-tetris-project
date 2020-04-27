# Setting up a development environment

It is recommended that you feel comfortable in whichever operating system you use for development. The bot runs on Ubuntu in production; I develop on Ubuntu as well, but dexfore does so on MacOS, and Xael on Windows with [WSL](https://docs.microsoft.com/en-us/windows/wsl/install-win10). Whichever you choose to use, it is expected that you know how to work with the command line at a basic level.

The first step is installing the necessary dependencies. For a quick setup, the only dependencies you need are python 3, pip3, and sqlite. On Ubuntu, the installation looks like this:

```bash
sudo apt install python3 python3-dev python3-pip sqlite3 libsqlite3-dev
```

On other \*nix distributions, replace `apt` with your package manager (`dnf`, `yum`, `pacman`, `brew`, or something else).

Once those are installed, click the "Fork" button in the top right of this page to make your own copy of the `classic-tetris-project` repository. Then, you can head into your shell and clone the repository:

```bash
git clone https://github.com/YOUR-USERNAME/classic-tetris-project
cd classic-tetris-project
```

Replacing "YOUR-USERNAME" with your actual GitHub username.

Once you're in the project directory, you can install project requirements and set up the database:

```bash
pip3 install -r requirements.txt
python3 manage.py migrate
```

Next, create your bot's accounts. For Discord, head to their [developer portal](https://discordapp.com/developers/applications) and click "New Application" in the top right. Once it's been created, head to the "bot" tab on the left and create a bot. Then, you'll be able to find the **token**. Additionally, make sure you have a Discord server in which you can test that bot (you need to have admin privs in a server to add a bot; I recommend creating a new server). Take note of that server's [ID](https://support.discordapp.com/hc/en-us/articles/206346498-Where-can-I-find-my-User-Server-Message-ID-), too; you'll need it, along with the token, for later.

For Twitch, create a standard Twitch account (different from your everyday account - I recommend doing this in either another browser or in private/incognito mode), then head to `https://twitchapps.com/tmi/`. TMI stands for "Twitch Messaging Interface", and that page will help you generate an **oauth key**, which you will need.

Finally, it's time to set up a `.env` file. This is the basic structure for that:

```
DISCORD_TOKEN=your_bots_discord_token
DISCORD_GUILD_ID=your_discord_guild_id

TWITCH_USERNAME=your_bots_twitch_username
TWITCH_TOKEN=your_twitch_oauth_key

TWITCH_CLIENT_ID=<ask me for this>
```

Once you have that in place (To be clear, it should be saved in a file called `.env` in the project's root directory), you can start up the bot:

```
python3 manage.py bot
```

To see if everything's working, the `!test` command should result in the bot enthusiastically responding with "Test!". (NOTE: on Twitch, do **not** attempt to invoke commands from the bot's account. Log into your normal Twitch account to test the bot.)  If you're getting errors, review the steps above.
