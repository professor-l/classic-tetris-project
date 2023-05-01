# The Classic Tetris Bot

This repository is a new and improved bot for Classic Tetris Monthly that is designed to be accessible to the whole community, both in and out of CTM contexts.  It is currently being run on a cloud computing instance rather than a home PC, and as such its uptime is drastically improved from the strikingly mediocre [former bot](https://github.com/professor-l/lsq-bot).

*See also: our newest Classic Tetris project, [ctdb](https://github.com/professor-l/ctdb)*

### Major Features

Here are some of the greater features the bot supports:

* Discord and twitch integration
* Account linking functionality
* Personal best tracking
* Other personal information storage (preferred name, country, etc.)
* A match queueing interface
* Miscellaneous commands (see [info.py](https://github.com/professor-l/classic-tetris-project/blob/master/classic_tetris_project/commands/info.py))
* A web interface at [go.ctm.gg](https://go.ctm.gg), providing web-based tournament orchestration tooling for CTM

A semi-full list of commands can be found in the [COMMANDS.md](https://github.com/professor-l/classic-tetris-project/blob/master/docs/COMMANDS.md) file.

### Community Input

We are also very open to community input, since that's of course the best way to improve a project like this. So feel free to [open an issue](https://github.com/professor-l/classic-tetris-project/issues) here on GitHub with any suggestions or bug reports. I also regularly check Discord, so if you don't have a GitHub account but have suggestions, I can be contacted there. The best place for suggestions is in the dedicated channel in the [CTM Discord Server](https://discord.gg/SYP37aV). You can also tag or DM me (I'm "Professor L" on Discord) _if something is urgent_. Just remember - I'm an amateur developer, not a professional, and this bot has been and continues to be a spectacular learning experience for me. So please be patient.

### Contributing

If you have familiarity with Python and Django and are looking to give more than suggestions, you might consider contributing to the bot's ever-growing codebase. I recently finished putting together a `/docs` directory that contains three highly valuable documents:

* [CONTRIBUTING.md](https://github.com/professor-l/classic-tetris-project/blob/master/docs/CONTRIBUTING.md): A guideline for those who wish to be either one-time, sporatic, or consistent contributors to our bot. We are _always_ looking for new team members.
* [ARCHITECTURE.md](https://github.com/professor-l/classic-tetris-project/blob/master/docs/ARCHITECTURE.md): A somewhat comprehensive outline of the layout of our codebase, our thoughts behind its design, and the basics of adding to it in a way that preserves scalability and growth.
* [SETUP_QUICK.md](https://github.com/professor-l/classic-tetris-project/blob/master/docs/SETUP_QUICK.md): An outline of what it takes to set up a development and testing environment, a necessary step if you want to submit pull requests and/or become a regular contributor.

Additionally, there exists a more comprehensive setup guide for those who intend to become regular contributors:
* [SETUP_ROBUST.md](https://github.com/professor-l/classic-tetris-project/blob/master/docs/SETUP_ROBUST.md): A guide to setting up a more robust development environment if the quick setup is insufficient.

## The team

Currently, the team consists of three people:

* **Professor L (Elle Nolan) - Co-head developer**: The bot's mother. I begun development of ClassicTetrisBot just a few weeks before my first NEStris maxout, in early January of 2019. It was originally written in a hurry, in Node.js. A dangerous combination. The code from that dark era is still public, if exclusively to provide a learning experience and encourage humility. _([Her GitHub](https://github.com/professor-l))_
* **dexfore (Michael Lin) - Co-head developer**: The bot's cool uncle who made it what it is today. He joined the team in May 2019, when I finally decided I needed to turn the bot's spaghetti code into something more reasonable. I brought him on because of his familiarity with a variety of technologies and techniques with which I was, at the time, relatively unfamiliar: relational databases, code infrastructure design, and Django, among many others. Without him, this bot would be nothing. _([His GitHub](https://github.com/michaelelin))_
* **Fireworks (Justin Hundley) - Contributor**: A new developer on the team as of 2022, who joined the community and immediately and eagerly began helping us out with all sorts of little hiccups and QoL things. He's been instrumental in this software suite's continued success over the last year. _([His GitHub](https://github.com/fireworks))_
