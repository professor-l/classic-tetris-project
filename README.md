# The Classic Tetris Bot

The Classic Tetris Bot is the de-facto utility for the Classic Tetris community.Originally created for Classic Tetris Monthly, it has substantially evolved beyond its [humble beginnings](https://github.com/professor-l/lsq-bot), belonging to 100 Discord severs, over 500 Twitch channels, and is used in both online and in-person tournaments.

Here are some of the greater features the bot supports:

* Discord and twitch integration
* Account linking functionality
* Personal best tracking
* Other personal information storage (preferred name, country, etc.)
* A match queueing interface
* Miscellaneous commands (see [info.py](classic_tetris_project/commands/info.py))
* A web interface at [go.ctm.gg](https://go.ctm.gg), providing web-based tournament orchestration tooling for CTM

A semi-full list of commands can be found in the [COMMANDS.md](docs/COMMANDS.md) file.

*See also: our newest Classic Tetris project, [ctdb](https://github.com/professor-l/ctdb)*

### Community Input

The most reliable way to leave feedback is through the project's [issue's page](https://github.com/professor-l/classic-tetris-project/issues) on Github with suggestions/bug reports. You can also reach out more directly through the [CTM Discord Server](https://discord.com/invite/ctm) or to any of the [team members](https://github.com/professor-l/classic-tetris-project/tree/master?tab=readme-ov-file#the-team) directly (e.g. to report an outage or ask for setup help).

### Contributing

If you have familiarity with Python and Django (or want to learn) and are looking to give more than suggestions, consider contributing to the bot's ever-growing codebase! You'll find useful references in the `docs/` directory:

* [CONTRIBUTING.md](docs/CONTRIBUTING.md): A guideline for those who wish to be either one-time, sporatic, or consistent contributors to our bot. We are _always_ looking for new team members.
* [ARCHITECTURE.md](docs/ARCHITECTURE.md): A somewhat comprehensive outline of the layout of our codebase, our thoughts behind its design, and the basics of adding to it in a way that preserves scalability and growth.
* [SETUP_QUICK.md](docs/SETUP_QUICK.md): An outline of what it takes to set up a development and testing environment, a necessary step if you want to submit pull requests and/or become a regular contributor.

Additionally, there exists a more comprehensive setup guide for those who intend to become regular contributors:
* [SETUP_ROBUST.md](docs/SETUP_ROBUST.md): A guide to setting up a more robust development environment if the quick setup is insufficient.

## The team

* **fractal (Justin Yu, `fractal161` on Discord) - Current Maintainer**: A longtime Classic Tetris player who first contributed to the project all the way back in [2020](https://github.com/professor-l/classic-tetris-project/pull/22), he's recently begun more work on adapting the bot to serve the community's modern needs. _([His GitHub](https://github.com/fractal161))_
* **Professor L (Elle Nolan, `professor_l` on Discord) - Co-creator**: The bot's mother. I begun development of ClassicTetrisBot just a few weeks before my first NEStris maxout, in early January of 2019. It was originally written in a hurry, in Node.js. A dangerous combination. The code from that dark era is still public, if exclusively to provide a learning experience and encourage humility. _([Her GitHub](https://github.com/professor-l))_
* **dexfore (Michael Lin, `dexfore` on Discord) - Co-creator**: The bot's cool uncle who made it what it is today. He joined the team in May 2019, when I finally decided I needed to turn the bot's spaghetti code into something more reasonable. I brought him on because of his familiarity with a variety of technologies and techniques with which I was, at the time, relatively unfamiliar: relational databases, code infrastructure design, and Django, among many others. Without him, this bot would be nothing. _([His GitHub](https://github.com/michaelelin))_
* **Fireworks (Justin Hundley, `fireworks` on Discord) - Contributor**: A Classic Tetris fan and seasoned developer who joined the community in 2022 and immediately and eagerly began helping us out with all sorts of little hiccups and QoL things. He's been instrumental in this software suite's continued success over the last year. _([His GitHub](https://github.com/fireworks))_

You should be able to find us through the [CTM Discord](https://discord.com/invite/ctm) if you ever need to reach out.
