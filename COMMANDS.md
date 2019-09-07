# Commands

The following is a detailed outline of each command the bot supports. As always, suggestions for more commands are welcome - you may open a [GitHub issue](https://github.com/professor-l/classic-tetris-project/issues/new) to suggest them as well as to report bugs in the existing ones.

Commands are listed with `<required parameters>` and `[optional parameters]`, which occasionally have a `[default=value]`.

## User commands

#### `!pb [username]`
**Platforms**: Twitch, Discord<br/>
**Aliases**: `!getpb`

Outputs the pb of the specified user, or you.

---
#### `!setpb <pb> [type=NTSC]`
**Platforms**: Twitch, Discord<br/>
**Aliases**: `!newpb`

Sets the given pb (of type NTSC or PAL) to yours in the database.

---
#### `!country [username]`
**Platforms**: Twitch, Discord<br/>
**Aliases**: `!getcountry`

Outputs the country of the specified user, or you.

---
#### `!setcountry <three-letter country code>`
**Platforms**: Twitch, Discord

Sets the specified country to yours in the database. You can find a list of the three-letter codes [here](https://www.iban.com/country-codes) under the "Alpha-3 codes" column.

---
#### `!name [username]`
**Platforms**: Twitch, Discord<br/>
**Aliases**: `!getname`

Outputs the preferred name of the specified user, or you.

---
#### `!setname <name>`
**Platforms**: Twitch, Discord

Sets your preferred name to the specified name. Can contain letters, numbers, spaces, hyphens, underscores, and periods.

---

## Account linking commands

Account linking is the newest feature of the bot, which comes with Discord integration. Using this command, you may link your twitch and Discord accounts through the bot so that the same data is being tracked for you regardless of the platform on which you update it. As more commands and features are added, this will provide additional benefits.

#### `!link <twitch username>`
**Platforms**: Discord<br/>
**Aliases**: `!linkaccount`<br/>
**Must be run in a private message**

Sends a whisper (on twitch) to the specified twitch user containing a **token** that can be used to link the two accounts. This **token** is then used in the `!linktoken` command to complete the account linking process.

---
#### `!linktoken <token>`
**Platforms**: Discord<br/>
**Must be run in a private message**

Links the twitch account specified in the `!link` command, provided that the **token** is the same one that was sent to the twitch user.  This means that to link an account, you must check your twitch whispers after sending the `!link` command and then input this token to the bot using this `!linktoken` command.

---
#### `!unlink`
**Platforms**: Twitch, Discord<br/>
**Must be run in a private message**

Whichever platform this is run on, it will unlink your account on that platform from all other accounts it has been linked to.  As of right now, only one Discord account can be associated with a twitch account, and vice versa.  However, this command will dissociate from *all other platforms* in the future (yes, there will eventually be other platforms).

---

## Queueing commands

#### `!queue`
**Platforms**: Twitch<br/>
**Aliases**: `!q`, `!matches`

Prints the entire queue into chat.

---
#### `!forfeit <index>`
**Platforms**: Twitch<br/>
**Must be run in a public channel**

Forfeits the match at the specified index, provided you are one of the players in that match.

---
#### `!match [user] [results=3]`
**Platforms**: Twitch<br/>
**Must be run in a public channel**

Retrieves the users in chat with personal bests closest to that of the specified user (or you). Displayes specified number of results.

---
#### `!challenge <user>`
**Platforms**: Twitch<br/>
**Must be run in a public channel**

Challenges the specified user to a match. Only one challenge can be pending to a user at a time, and each user may only issue one challenge at a time.

---
#### `!accept`
**Platforms**: Twitch<br/>
**Must be run in a private message**

Accepts the pending challenge to you, if there is  one, and adds that match to the queue.

---
#### `!decline`
**Platforms**: Twitch<br/>
**Must be run in a private message**

Declines the pending challenge to you, if there is one.

---
#### `!cancel`<br/>
**Platforms**: Twitch<br/>
**Must be run in a public channel**

Cancels your pending challenge to someone else, if you have issued one.

---
### Moderator-only

#### `!open`
**Platforms**: Twitch<br/>
**Aliases**: `!openqueue`<br/>
**Must be run in a public channel**
**Moderator-only**

Opens the queue. This both allows players to challenge one another and allows moderators to add matches manually.

---
#### `!close`
**Platforms**: Twitch<br/>
**Aliases**: `!closequeue`<br/>
**Must be run in a public channel**
**Moderator-only**

Closes the queue. This prevents challenges from being issued or accepted. Moderators may no longer add matches to the queue unless they reopen it.

---
#### `!addmatch <player 1> <player 2>`
**Platforms**: Twitch<br/>
**Must be run in a public channel**
**Moderator-only**

Adds a match between the two specified players to the queue.

---
#### `!removematch <index>`<br/>
**Platforms**: Twitch<br/>
**Must be run in a public channel**
**Moderator-only**

Removes a match at the specified index from the queue.

---
#### `!clear`
**Platforms**: Twitch<br/>
**Aliases**: `!clearqueue`<br/>
**Must be run in a public channel**
**Moderator-only**

Clears the entire queue.

**NOTE**: This command must be run as `!clear yesimsure` (Yes, I'm sure) to be certain that you didn't type this command by accident.

---
#### `!winner <player> [losing score]`
**Platforms**: Twitch<br/>
**Aliases**: `!declarewinner`<br/>
**Must be run in a public channel**
**Moderator-only**

Declares the specified player the winner of a game, and stores that result (as well as the optionally provided losing score) in the current match data.

---
#### `!endmatch`
**Platforms**: Twitch<br/>
**Must be run in a public channel**
**Moderator-only**

Ends the current match, automatically determining the winner based on the match data stored each time `!winner` was called.

## Other commands

#### `!summon`
**Platforms**: Twitch<br/>
**Must be run in a private message**

Call this command in a whisper to the bot to add the bot to your channel.

---
#### `!pleaseleavemychannel`
**Platforms**: Twitch<br/>
**Must be run in a private message**

Call this command in a whisper to the bot to remove the bot from your channel.

---
#### `!3`
**Platforms**: Twitch

Counts down from 3 before saying "Tetris!" in the chat. Works for any number from 3-10.

---
#### `!help`
**Platforms**: Twitch, Discord

Links the user to this page.
