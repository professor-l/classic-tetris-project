# ClassicTetrisBot's Architecture

ClassicTetrisBot (CTB) as we designed it takes advantage of [object-oriented programming (OOP)](https://en.wikipedia.org/wiki/Object-oriented_programming), a paradigm with a rich history and a diverse set of practical applications. Specifically, it is written in [Python](https://www.python.org) and uses the popular Python web framework [Django](https://www.djangoproject.com). It also utilizes a [relational database](https://en.wikipedia.org/wiki/Relational_database) to store information about users. If you are unfamiliar with any of these things, I recommend doing some research before you continue.

### Philosophy

We designed this codebase from the ground up, and in doing so we had to repeatedly ask ourselves the most important question of all large projects, regardless of scope: **What do we want this to do?** This may seem trivial or obvious, but in the heart of a lengthy discussion it can be easily forgotten, and keeping it in mind is key. The only question of comparable importance is as follows: **How will this design hold up over time?** Essentially, without being unreasonable, we tried to leave as many doors open as possible. With a project as open-ended as CTB, a restrictive design could easily come back to bite us in the butt.

With these two points in mind, using our tools at hand, this is what we came up with.

## The Beginnings

This is, first and foremost, a chatbot. It needs to be able to read and send messages. So our very first step is to figure out what we need to make that happen. Usually, depending on the platform(s), that means installing a library that communicates with their API. Finding [discord.py](https://discordpy.readthedocs.io/en/latest/index.html) wasn't tough, but Twitch was a bit tougher. The few options we found seemed suboptimal for our purposes. Luckily, Twitch chat is built on top of [Internet Relay Chat (IRC)](https://en.wikipedia.org/Internet_Relay_Chat), a tried-and-true protocol that predates NEStris itself. Python has an [IRC library](https://python-irc.readthedocs.io/en/latest/index.html), but it's not especially comprehensive, and while Twitch chat utilizes the IRC protocol, it has its own idiosyncrasies (whispers, for instance). So, in order to properly communicate with Twitch chat, we (mostly dexfore) wrote out [twitch.py](https://github.com/professor-l/classic-tetris-project/blob/master/classic_tetris_project/twitch.py). Because modular code works well with OOP (and because it typically lends itself well to scaling), we wrote twitch.py as a series of small classes that interact with and build upon one another. 

With the basics of communicating with Discord and Twitch chat individually tackled, our next logical task was getting both to work simultaneously. This, however, proved almost immediately to be nontrivial.

### The Duality of Robot

We were porting this bot from Node.js, and despite its shortcomings, Node is known for being event-driven and, more importantly, asynchronous. Python is not async by default, but async functions can be written and `await`ed. However, mixing synchronous and asynchronous code can be dangerous. Trying to call an async function without `await`ing it makes Python complain, which is bad. But trying to call a synchronous function from an asynchronous one is far worse.

The purpose of running code asynchronously is to get something done while allowing the main event loop to continue doing what it does best - handling events. However, if you call a time-consuming _synchronous_ function (like a database query through the Django ORM) from within a coroutine, there's nothing telling Python to give it its own coroutine; contrarily, because the function is synchronous, it actually implicitly instructs Python to run it in the main event loop. This, as you may have realized, can be problematic.

To make matters worse, the `discord.py` library is written asynchronously. This seems nice, but what if we want to make a database call between receiving a message and giving our response - for instance, if someone queries a PB or a profile? The solution is to dispatch synchronous functions in a new thread, which allows them to be `await`ed from within async functions without blocking the event loop. Basically, we _explicitly_ tell Python to run them in a coroutine rather than the event loop.

Because the `twitch.py` code is synchronous, however, in order to separate it from the event loop (as `discord.py` had already done for us), we used Python's built-in [threading library](https://docs.python.org/3/library/threading.html) to give the entire Twitch event listener its own thread, separating the event loop from both the Discord and Twitch bots. This is exactly what we want - an event loop that can continue to run, even if an individual Twitch or Discord command stalls briefly.

## Commands

At the core of a chatbot lie the commands. We wanted to make adding new commands as easy as possible, which meant laying a strong foundation for them. Our plan was to give each command its own class, creating instances of the classes and running their `execute` methods when they were run from Twitch or Discord. In the spirit of OOP, we decided to make a `Command` superclass (see [command.py](https://github.com/professor-l/classic-tetris-project/blob/master/classic_tetris_project/commands/command.py)), from which all command classes would inherit. Additionally, we had a separate `CommandContext` class that later became a superclass for `TwitchCommandContext` and `DiscordCommandContext` (see [command\_context.py](https://github.com/professor-l/classic-tetris-project/blob/master/classic_tetris_project/commands/command_context.py)). The `CommandContext` class contains meta-information of a command - such as who called it and where - as well as helper methods like `send_message`. The more robust `Command` superclass has a `context` property, along with many more fields and methods, most of which are named verbosely enough to be understood, and all of which are intended to be theoretically useful to a wide variety of actual commands.

Perhaps most notably, the `Command` class contains:

* A `check_support_and_execute` method that, among other things, takes the `args` array from its context and distributes its contents out to the explicit, named arguments of its `execute` method, catching any argument errors and raising necessary exceptions in the process.
* A static method called `register` that registers commands with specific keywords and platforms using the `COMMAND_MAP` dict, subsequently defining how they are used on the user's side. `Command.register` is a [decorator](https://en.wikipedia.org/wiki/Python_syntax_and_semantics#Decorators) for all command class definitions. This means that it acts as a higher-order function, being automatically called every time it is used above a class definition.

Due in  part to these two key features, this is what it would look like to create a command called `!example` that took a username as an argument:

```python
# Importing the superclass
from .command import Command

# Applying the decorator
@Command.register("example", usage="example <user>")
class ExampleCommand(Command):
  def execute(self, username):
    """
    execution code
    goes here
    """
```

Having a separate class for each command provides several advantages, many of which we have utilized in at least some of the commands we've implemented:

* In the case of the various [queuing commands](https://github.com/professor-l/classic-tetris-project/blob/master/classic_tetris_project/commands/matches/queue.py), we found that they could all benefit from sharing their *own* superclass beneath `Command`, which we called `QueueCommand`. This superclass still extends `Command`, but it provides additional functionality to its subclasses, including an interface for manipulating the queue itself.
* For more complex commands, notably the [summon command](https://github.com/professor-l/classic-tetris-project/blob/master/classic_tetris_project/commands/summon.py), having the code for execution defined in a method rather than a standalone function allows us to define helper methods that clean up the code within `execute` without any ambiguity as to the purpose or practical scope of those methods.

Tangentially, the advantage of Python over Java (other than, you know, all of them) with a structure like this is that we can define separate but related classes (like the get/set commands for a particular database field like PB or playstyle)  in the same file.

When all of this comes together, we end with a relatively seamless process for adding new commands to the bot. Create a new class - in a new file, when appropriate - complete with a decorator and an execute function.

## The Database

With the command infrastructure in place, there was only one more major step before we could dive into feature development: the database. The former bot, because it was thrown together, because it had a small-ish userbase, and because Node.js ORM options are lacking, the original bot didn't use a database - it simply read and wrote JSON files that stored people's PBs or wins/losses. In programmers' circles, we call that "stupid." It did the j ob, but it didn't do it well, and it certainly wasn't sustainable.

In the spirit of scalability, in construction of our new bot we decided to use a relational database. You know, properly. The advantage of using Django is that we have access to not only a decent [object-relational mapping tool (ORM)](https://en.wikipedia.org/wiki/Object-relational_mapping), but also a [migration](https://en.wikipedia.org/wiki/Schema_migration) management tool. Briefly, an **ORM** allows us to make database queries without writing raw SQL, and migrations are what allow us to change the structure of our database in a safe and systematic manner while maintaining identical database structures in all our development environments.

The difficult part of designing our database was managing the bot's dual presence on both Twitch and Discord. We wanted to account for the possibility that we may have some users on only one of the two platforms, and some on both. To get around this, we elected to write a `User` model that was *separate* from the `TwitchUser` and `DiscordUser` models (see the models' [source code](https://github.com/professor-l/classic-tetris-project/blob/master/classic_tetris_project/models/users.py). Each Twitch and Discord user has a foreign key field pointing to the `User` model, which stores all meaningful data. This permits the account linking function we sought to implement, whereby people can update their data on either Twitch or Discord, and changes will be tracked on both platforms. It also has the added advantage of leaving doors open for further platform user models, should we ever add support for another.  We also have a `TwitchChannel` model for each channel on Twitch to which the bot has been summoned.

The other function the database serves is storing match results, which introduces another hurdle: matches don't have a set number of games. Best-of-3 and best-of-5 are the two most common formats, but even then, a BO5 could have three games in a sweep or five with a decider. To address this, we added both `Match` and `Game` models, each with different fields. The `Match` table stores the two players (foreign keys to the `User` table), the two win counts, and other match metadata. Each `Game` has a foreign key to the `Match` of which it was a part, as well as a winner and an optional losing score. This structure allows the association of arbitrary numbers of `Game`s with a single `Match`.

This database was our final major hurdle, and once we cleared it we begun aggressively implementing each of the commands on our list of necessities. From there, it rapidly evolved into production-ready software, and once we had our foundations in place, we commenced with rollout.

## Other Foundations

In building a house, you can make renovations and enhancements on the existing structure without extensively reworking everything. Adding new electrical outlets consists of connecting more wires to the existing electrical system of the house; replacing a sink or toilet requires only that you connect the new apparatus to existing pipes. Adding an external addition to the building, however, requires you to lay additional foundation. New additions, constructed properly, emulate the style and features of the rest of the house and connect to the same underlying infrastructure - electric, plumbing, or heat, for instance - but also provide new rooms that serve new purposes.

Excusing the extended metaphor, this is the philosophy to which we subscribe in adding new features that need their own foundational code. Once the additions are complete, we want them to semi-seamlessly integrate with the rest of the code, or at the very least to play nice with it. We want it to look no different than what we've done already, in the same way that a home addition should not be immediately recognizable as "new" to the average homeowner once it is complete.

### Moderation

The only real addition we've made thus far that has required any kind of foundation beyond what we had was the moderation feature. It came about when we added an #all-caps channel to the [CTM Discord Server](https://discord.gg/SYP37aV). I wanted the bot to delete all messages with lowercase letters in them, including edited messages. Adding a feature like this, something that actually required a new Discord API event listener in the [management bot.py](https://github.com/professor-l/classic-tetris-project/blob/master/classic_tetris_project/management/commands/bot.py). The full list of events on the `discord` class can be found [here](https://discordpy.readthedocs.io/en/latest/api.html#event-reference), but we already had a listener for `on_message` - which just needed to be altered - and I only needed to add one for `on_message_edit`. 

In the spirit of consistency, I wanted the code for moderation in the management file to look as similar as possible to the nearby code for command recognition and dispatch. This meant structuring moderation rules similarly to commands - we have a `DiscordModerator` class with metadata and mid-level helper methods (analogous to the `CommandContext` class), and a `DiscordRule` superclass with more abstract methods useful for specific rules. The moderation rule classes (of which there is currently only one) will each be subclasses of the aforementioned `DiscordRule`, just as specific command classes are subclasses of the `Command` superclass.

Previously, the structure was less robust - there weren't as many files, but the layout left much to be desired. However, in writing this very section, it dawned on me that what we had could be improved, so I did [just that](https://github.com/professor-l/classic-tetris-project/commit/077663895886f7eca881f2ce70aaf0d1ac1be9be).

### Website

The bot's web interface initially started as a private [submodule](https://git-scm.com/book/en/v2/Git-Tools-Submodules), but has since been open sourced to the project's [web/](classic_tetris_project/web) directory. I (fractal) don't know too much about this so this section may be expanded upon.

### Looking Forward

A number of minor improvements can be found in this [to-do list](https://github.com/professor-l/classic-tetris-project/projects/1). However, in the years since it was last updated, the scope of the bot and the needs of the community have expanded, so a [new list](https://github.com/users/professor-l/projects/2) was created to reflect these broader goals. However, many possible features remain unknown to us. We take suggestions and input from the community, and when inspiration strikes, we jump on it, and that has created a very open-ended project. That's another reason we welcome contributors - the more minds we have, the more diverse our set of perspectives, the better our software will be.
