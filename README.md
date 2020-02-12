# The Classic Tetris Bot

This repository is a new and improved bot for Classic Tetris Monthly that is designed to be accessible to the whole community, both in and out of CTM contexts.  It is currently being run on a cloud computing instance rather than a home PC, and as such its uptime is drastically improved from the strikingly mediocre [former bot](https://github.com/professor-l/lsq-bot).

### Major Features

Here are some of the greater features the bot supports:

* Discord and twitch integration
* Account linking functionality
* Personal best tracking
* Other personal information storage (preferred name, country, etc.)
* A match queueing interface
* Miscellaneous commands (see [info.py](https://github.com/professor-l/classic-tetris-project/blob/master/classic_tetris_project/commands/info.py)
* More to come - including a web interface, the development of which is just beginning

A full list of commands can be found in the [COMMANDS.md](https://github.com/professor-l/classic-tetris-project/blob/master/COMMANDS.md) file.

### Community Input

We are also very open to community input, since that's of course the best way to improve a project like this. So feel free to [open an issue](https://github.com/professor-l/classic-tetris-project/issues) here on GitHub with any suggestions or bug reports. I also regularly check Discord, so if you don't have a GitHub account but have suggestions, I can be contacted there. The best place for suggestions is in the dedicated channel in the [CTM Discord Server](htpps://discord.gg/SYP37aV). You can also tag or DM me (I'm "Professor L" on Discord) _if something is urgent_. Just remember - I'm an amateur developer, not a professional, and this bot has been and continues to be a spectacular learning experience for me. So please be patient.

### Contributing

If you have familiarity with Python and Django and are looking to give more than suggestions, you might consider contributing to the bot's ever-growing codebase. I am currently putting together `/docs` directory that will contain, among other things, the following:

* `ARCHITECTURE.md`: A somewhat comprehensive outline of the layout of our codebase, our thoughts behind its design, and the basics of adding to it in a way that preserves scalability and growth.
* `CONTRIBUTING.md`: A guideline for those who wish to be either one-time, sporatic, or consistent contributors to our bot. We are _always_ looking for new team members.
* `SETUP.md`: A detailed outline of what it takes to set up a development and testing environment, a necessary step if you want to submit pull requests and/or become a regular contributor.

## The team

Currently, the team consists of two people:

* **Professor L (Elle Nolan) - Co-head developer**: The bot's mother. I begun development of ClassicTetrisBot just a few weeks before my first NEStris maxout, in early January of 2019. It was originally written in a hurry, in Node.js. A dangerous combination. The code from that dark era is still public, if exclusively to provide a learning experience and encourage humility. _([Her GitHub](https://github.com/professor-l))_
* **dexfore (Michael Lin) - Co-head developer**: The bot's cool uncle who made it what it is today. He joined the team in May 2019, when I finally decided I needed to turn the bot's spaghetti code into something more reasonable. I brought him on because of his familiarity with a variety of technologies and techniques with which I was, at the time, relatively unfamiliar: relational databases, code infrastructure design, and Django, among many others. Without him, this bot would be nothing. _([His GitHub](https://github.com/michaelelin))_
