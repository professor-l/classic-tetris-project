# Contributing to ClassicTetrisBot 

From the beginning - even with the old Node.js bot - this project has been open source, licensed under the highly permissive MIT license. I want everyone to be able to see the code, but I also want anyone to be able to run it, mess with it, and break it.

There are several advantages to this, but the two most important ones are as follows:

1. The more opinions we get, the more eyes on our code, the better the project will be. Anyone can look for bugs, suggest changes to implementation or structure, suggest features, and otherwise comment on the code. Ideally, if I do something exceptionally stupid, at least one person will notice and say something. Or at least, that's the goal.
2. I'm not binded to this project. I think this is even more important than the first point. If, in a few months or years, I decide I no longer want to actively maintain and improve the bot, I don't have to. I could announce my planned departure, and within as little as a few hours, another community member could set up an AWS instance, clone this repository, and do the minimal setup required to keep the bot running in my absence. Even in a worst-case scenario where I'm not around to transfer ownership or oauth keys, the code itself is here; you'd only need another Twitch account. 

## A Guide to Contribution

We have two tiers of people whose code appears somewhere in this repository:

1. **Contributors** are people who have submitted at least one PR here *that I accepted*. Contributors get a "developer" role in my [Discord server](https://discord.gg/KJf9grF) for developing and testing new features. Fancy blue name!

2. **Team members** are people who have earned my trust by submitting a significant number of PR's or a few larger ones. These people will be determined subjectively and on a case-by-case basis. Team members receive:
    * A "Bot Technician" role in the [official CTM Discord server](https://discord.gg/SYP37aV)
    * A sudo-enabled user account on the bot's AWS EC2 instance, which comes with access to the joint `dev` user and the `bot` user, under which the production bot is running
    * Oauth tokens for the Discord and Twitch *test bots*

However, as a fully-fleged team member, you are also expected to be another potential responder in the case of an outage or urgent bug report. At least 95% of the time, all this entails is restarting the bot on AWS (with a computer and an internet connection, this can be done in under a minute). You should also, ideally, spend at least a few hours each week doing some bot-related work. Admittedly, dexfore and I have both been slacking on this lately because the bot is in a good place right now and our next step is kind of a big one, but this is a general guideline.

Those looking to become team members should start by contributing something small. There is a to-do list of small planned additions on this repo's [project page](https://github.com/professor-l/classic-tetris-project/projects/1). Picking something from there is a great way to sumbit a small first PR, but before jumping into that, it's a good idea to take a look at a few markdown documents aside from this one:
* [README.md](https://github.com/professor-l/classic-tetris-project/blob/master/README.md): Yes, it's just the readme, but please actually read it (or finish reading it) if you haven't already. 
* [ARCHITECTURE.md](https://github.com/professor-l/classic-tetris-project/blob/master/docs/ARCHITECTURE.md): A long(ish) write-up detailing our design process of this bot's architecture. It's written like a blog to make it a little more bearable (and beacuse I hate writing purely technical documentation).
* [SETUP.md](https://github.com/professor-l/classic-tetris-bot/blob/master/docs/SETUP.md): A guide to setting up a development environment. It's not for the faint of heart; expect to set aside at least thirty minutes for this if you're an experienced developer, and an hour or more if you're more of a beginner.

Once you've read (and I mean *really* read) those pages, you should be prepared to submit your first pull request. Write your code, submit the PR, and DM me on Discord to let me know that it's waiting my approval. Best of luck!
