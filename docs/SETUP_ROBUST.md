# Setting up a development environment

In the case of a bot like this, when we implement new features, we test them on a completely separate bot before pushing them to production. This means a separate Twitch account, a separate Discord bot on a separate Discord server, and a separate database. This has numerous advantages, but unfortunately it can be a bit of a pain to set up. This document will outline that process.

## Preliminaries

The bot runs on an Amazon Web Services (AWS) [EC2 instance](https://aws.amazon.com/ec2). AWS is highly reliable, runs 24/7, and most importantly allows us to dynamically scale the resources as necessary. When I first joined the CTM server, it was quite literally less tha 1% of its current size. This bot started out on Twitch only, without a `!summon` command, and was in only one channel aside from [its own](https://www.twitch.tv/classictetrisbot): the [ClassicTetris channel](https://www.twitch.tv/classictetris). Today, it is in over 120. Scalability is important - as the Tetris community continues to grow (and as this project and the corresponding [website](https://monthlytetris.info) do so alongside it), we will need room to expand not only the software but the hardware infrastructure as well.

The AWS instance is running under the Ubuntu 18.04 LTS server distribution, but for development, I'm confident that any \*nix operating system will do. However, if you have Windows, you may consider [Windows Subsystem for Linux (WSL)](https://docs.microsoft.com/en-us/windows/wsl/install-win10), which allows you to run many Linux distributions, including Ubuntu 16.04 and 18.04, from your Windows machine. WSL can be finnicky, but it works well enough for this.

Once you have access to sudo priviliges in a bash command line with which you are relatively comfortable, you can proceed. For the following instructions, I use `apt` as a package manager, but you may replace that with whatever your operating system uses (`dnf`, `yum`, `pacman`, and `brew` are a few examples).

## Setup

### Development dependencies

Begin, if you haven't already, by installing the necessary packages with your package manager:

```bash
sudo apt install python3.7 python3.7-dev python3-pip sqlite3 libsqlite3-dev
```

For a robust development environment, next, using Python's package manager [pip](https://pip.pypa.io/en/stable), we install [virtualenvwrapper](https://virtualenvwrapper.readthedocs.io/en/latest), which is "a set of extensions" of another Python tool called virtualenv. Its benefits are numerous, but most notably it elegantly (and quietly) deals with versioning of all dependencies, as well as of Python itself, within our development and production environments. Install it like so:

```bash
sudo pip install virtualenvwrapper
source /usr/local/bin/virtualenvwrapper.sh
```

Alternatively, with Python 3:

```bash
sudo pip3 install virtualenvwrapper
VIRTUALENVWRAPPER_PYTHON="/usr/bin/python3"
source /usr/local/bin/virtualenvwrapper.sh
```

### Directory and Virtualenv Setup

Now, make sure you're logged in to your GitHub account, and **fork this repository** using the button at the top right of this page. This will create a *copy* of the repository on your GitHub account, allowing you to commit and push your changes without altering my repository.

Next, back in your command line, clone your new forked repository (replacing `YOUR-USERNAME` in the following command with your GitHub username) and enter the directory:

```bash
git clone https://github.com/YOUR-USERNAME/classic-tetris-project.git
cd classic-tetris-project
```

Now, we can make a virtual environment with the previously installed tool. I called mine `ctp`, short for Classic Tetris Project. Because this bot runs on Python 3.7, we direct the virtual environment to use that version (Which should now be installed) with the `--python` flag:

```bash
mkvirtualenv ctp --python=/usr/bin/python3.7
```

After running that, there should be a `(ctp)` preceeding the bash prompt on your screen. Mine looks like this:

```
(ctp) elle@home-dev-server:classic-tetris-project$
```

Every time you restart the bash session, when you enter the repository to develop or test, you have to remember to type `workon ctp` to also enter the virtual environment you've created. Errors will arise if you do not, because your machine will try to run the bot under Python 2.7.

### Development Requirements and Database Setup

From within the project's root directory (`classic-tetris-project`), run the following command to install the requirements:

```bash
pip install -r requirements.txt
```

This will install the 
We're almost done! We just have two more steps. Right now, there's still no database at all (or, if you took the optional steps, the database is empty). Thankfullly, with SQLite, there's no setup involved, because Django will automatically create a database upon the first migration if one doesn't exist already. Still within the project's root directory, run this:

```bash
python manage.py migrate
```

It should apply a series of migrations with cryptic names that create your database and structure it properly.

### Creating Platform Bot Accounts

Now, we're ready to create your bot accounts. These are the accounts that your bot will use to communicate.

#### Twitch

First, create a **new Twitch account** that will act as your bot for testing. My test account is called ClassicTetrisBotTest, but you can call yours anything you want. I recommend doing this in a private browsing/incognito window (or in a browser you don't normally use for Twitch) so you don't have to log out of your actual Twitch account.

Next, in the same browser window (logged in to new account), head to `https://dev.twitch.tv`. Click "Log in with Twitch" in the top right, and then "Authorize" on the subsequent page. When you're redirected back to the dev homepage, click on the "Your Console" button in the top right (right where the login button used to be). On the right, in the Applications panel, click "Register Your Application". The *Name* field can be whatever you want, but you should add `http://localhost` as an *OAuth Redirect URL*, and the *Category* should be "Chat Bot". Complete the captcha and click "Create". Then, click "Manage", and **copy and store the contents of the Client ID field and label it as such.** 

Finally for our Twitch setup, we need an OAuth token to be used for API calls and for chat functionality.  To do this, we can follow the steps outlined here: https://dev.twitch.tv/docs/authentication/getting-tokens-oauth/#oauth-implicit-code-flow.  Note that this is the preferred way to generate a token as opposed to third party token generation apps as we must ensure our oauth token matches our client ID for the Twitch Helix API. The following get request will suffice (replace client_id with your client ID):

```
https://id.twitch.tv/oauth2/authorize?client_id={client_id}&redirect_uri=http://localhost&response_type=token&scope=chat:read chat:edit moderator:read:chatters
```

That will return a URL with an access token on it. **copy it into a text document or otherwise save it for later**.

Aside: you'll notice a number of *scopes* that are part of the url. These are permissions that the bot needs from Twitch. Here's what they all mean:
- `chat:read` - view chat messages, so it can receive commands.
- `chat:edit` - send chat messages, to respond to commands.
- `moderator:read:chatters` - view the list of users currently viewing a channel that the bot is a moderator of. Used for commands like `!match`.

#### Discord

Now, we can move on to Discord. Back in your usual browser, make sure you're logged in to [Discord](https://discordapp.com), then head to their [developer portal](https://discordapp.com/developers/applications). Click "New Application" in the top right, and give it any name you wish; both my production and test applications have identical names to their Twitch counterparts. Once you've created the application, take a minute to explore the interface if you so desire, then head to the "Bot" section on the left. There should be an "Add Bot" button that's just *begging* to be clicked.

By default, the bot you create has the same username as the name of your project, but it is of course editable at any point. What you're interested in is the *token*. There should be a TOKEN label directly beneath the username of your bot. Click the "Copy" button right there, which copies the token to your clipboard, and paste it in the same place as your Twitch OAuth key and Client ID, making sure to keep everything labeled so you know what's what.

After this, scroll down to the "Privileged Gateway Intents" section and enable the "Server Members Intent" option.

Next, head to the OAuth tab on the left, and check the permission boxes exactly according to the following images:

![OAuth Permissions](https://github.com/professor-l/classic-tetris-project/blob/master/docs/img/oauth_permissions.png)

![Bot Permissions](https://github.com/professor-l/classic-tetris-project/blob/master/docs/img/permissions.png)

Then, copy the URL given at the bottom of the OAuth permissions box (the first one) and save it sommewhere (only briefly - you can just paste it in a new tab if you want).  Finally, back on the Discord app, create a [new server](https://support.discordapp.com/hc/support/en-us/articles/204849977-How-do-I-create-a-server-) to use as your testing server. 

Head back to that URL you just saved, and enter it into your browser. When asked which server(s) you want to add the bot to, select the new one you just made, and click "Continue" followed by "Authorize". You may have to convince them that you're not a robot, but hopefully you're not a robot, in which case that shouldn't be an issue. If it is... talk to me, and we may be able to work somethiing out.

One last step on Discord - go into your settings in Discord itself, head into the "Appearance" section, and **enable developer mode**. This will allow you to copy IDs and other things that will be useful for you as a - wait for it - *developer*. Once that's done and you've saved your changes, you're set!

### Environment Variables

Okay, I *promise* we're almost done. We just have one more step.

Back in the `classic-tetris-project` directory, either using a command-line or GUI text editor, create a new file in the root directory called `.env`. This file will store environment variables on which the bot depends. Fill out the file like so:

```
DISCORD_TOKEN=<Your Discord token>
DISCORD_GUILD_ID=<Your new Discord server's ID>

TWITCH_USERNAME=<Your Twitch bot's username>
TWITCH_TOKEN=<Your Twitch OAuth token (excluding the "oauth" prefix)>
TWITCH_CLIENT_ID=<Your Twitch Client ID>
```

You can optionally add `DISCORD_MODERATOR_ROLE_ID`, which should correspond with the role that people must have to invoke moderator-only commands on Discord, but it is not necessary.

To get the guild/server ID, right-click on the server's icon and click "Copy ID" (if it's not an option, you forgot to enable Developer Tools in settings).

### Running the Bot

Now, save that `.env` file, and you should - *finally* - be ready for a test run. In the command line, inside the virtual environment you've created, run:

```bash
python manage.py bot
```

If that connects to your bot's Twitch channel as well as Discord (and confirms these connections in the shell), everything's working! Try pinging the bot with a quick `!test` - it should respond enthusiastically. You can also test the databse's functionality by setting your PB and even linking your Twitch account, keeping in mind that this is running on a test database, and there are no consequences to losing that data.  

If something goes wrong, read the error message carefully, and see if you can troubleshoot. I am also happy to help - if you've made it this far, you're dedicated enough to be worth my time - so don't hesitate to reach out to me (Professor L#1975) on Discord!

Most importantly, if you have any remarks on this setup guide, you're welcome to suggest edits or ask questions to help with clarity or even fix bugs. This should provide you with a good starting point for development, but nothing is permanent, and nothing is above criticism. Especially here.
