# ClassicTetrisBot's Architecture

ClassicTetrisBot (CTB) as we designed it takes advantage of [object-oriented programmning (OOP)](https://en.wikipedia.org/wiki/Object-oriented_programming), a paradigm with a rich history and a diverse set of practical applications. Specifically, it is written in [Python](https://www.python.org) and uses the popular Python web framework [Django](https://www.djangoproject.com). It also utilizes a [relational database](https://en.wikipedia.org/wiki/Relational_database) to store information about users. If you are unfamiliar with any of these things, I recommend doing some research before you continue.

### Philosophy

We designed this codebase from the ground up, and in doing so we had to repeatedly ask ourselves the most imoprtant question of all large projects, regardless of scope: **What do we want this to do?** This may seem trivial or obvious, but in the heart of a lengthy discussion it can be easily forgotten, and keeping it in mind is key. The only question of comparable importance is as follows: **How will this design hold up over time?** Essentially, without being unreasonable, we tried to leave as many doors open as possible. With a project as open-ended as CTB, a restrictive design could easily come back to bite us in the butt.

With these two points in mind, using our tools at hand, this is what we came up with.

## The Beginnings

This is, first and foremost, a chatbot. It needs to be able to read and send messages. So our very first step is to figure out what we need to make that happen. Usually, depending on the platform(s), that means installing a library that communicates with their API. Finding [discord.py](https://discordpy.readthedocs.io/en/latest/index.html) wasn't tough, but Twitch was a bit tougher. The few options we found seemed suboptimal for our purposes. Luckily, Twitch chat is built on top of [Internet Relay Chat (IRC)](https://en.wikipedia.org/Internet_Relay_Chat), a tried-and-true protocol that pre-dates NEStris itself. Python has an [IRC library](https://python-irc.readthedocs.io/en/latest/index.html), but it's not especially comprehensive, and while Twitch chat utilizes the IRC protocol, it has its own idiosyncracies (whispers, for instance). So, in order to properly communicate with Twitch chat, we (mostly dexfore) wrote out [twitch.py](https://github.com/professor-l/classic-tetris-project/blob/master/classic_tetris_project/twitch.py). Because modular code works well with OOP (and because it typically lends itself well to scaling), we wrote twitch.py as a series of small classes that interact with and build upon one another. 

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

* In the case of the various [queueing commands](https://github.com/professor-l/classic-tetris-project/blob/master/classic_tetris_project/commands/matches/queue.py), we found that they could all benefit from sharing their *own* superclass beneath `Command`, which we called `QueueCommand`. This superclass still extends `Command`, but it provides additional functionality to its subclasses, including an interface for manipulating the queue itself.
* For more complex commands, notably the [summon command](https://github.com/professor-l/classic-tetris-project/blob/master/classic_tetris_project/commands/summon.py), having the code for execution defined in a method rather than a standalone function allows us to define helper methods that clean up the code within `execute` without any ambiguity as to the purpose or practical scope of those methods.

Tangentially, the advantage of Python over Java (other than, you know, all of them) with a structure like this is that we can define separate but related classes (like the get/set commands for a particular database field like PB or playstyle)  in the same file.

When all of this comes together, we end with a relatively seemless proccess for adding new commands to the bot. Create a new class - in a new file, when appropriate - complete with a decorator and an execute function.

## The Database

TODO

## Other Foundations

TODO

### Moderation

TODO

### The Admin Web Interface

TODO

### Looking Forward

TODO
