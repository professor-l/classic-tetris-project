# Commands

The following is a detailed outline of each command the bot supports. As always, suggestions for more commands are welcome - you may open a [GitHub issue](https://github.com/professor-l/classic-tetris-project/issues/new) to suggest them as well as to report bugs in the existing ones.

Commands are listed with `<required parameters>` and `[optional parameters]`, which occasionally have a `[default=value]`.

## User commands

#### `!profile [username]`
**Platforms**: Discord<br/>

Prints most standard information stored in the bot belonging to the specified user, or yourself if no argument is provided. Also makes it pretty.

#### `!pb [username]`
**Platforms**: Twitch, Discord<br/>
**Aliases**: `!getpb`

Outputs the pb of the specified user, or yourself if no argument is provided.

---
#### `!setpb <pb> [type=NTSC] [level=18]`
**Platforms**: Twitch, Discord<br/>
**Aliases**: `!newpb`

Sets the given pb (of type NTSC, 19/NTSC19, or PAL) to yours in the database.

---
#### `!setplaystyle <DAS|Hypertap|Hybrid>`
**Platforms**: Twitch, Discord<br/>
**Aliases**: `!setstyle`

Sets your playstyle to DAS, Hypertap, or Hybrid.

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
#### `!samepieces [username]`
**Platforms**: Twitch, Discord<br/>
**Aliases**: `!samepiecesets`

Outputs whether the specified user (or you) can use the same piece sets romhack.

---
#### `!setsamepieces <Y/N>`
**Platforms**: Twitch, Discord<br/>
**Aliases**: `!setsamepiecesets`

Sets your ability to run HydrantDude's same piece set romhack. Options are y/yes/t/true and n/no/f/false.

---

## Account linking commands

Account linking is the newest feature of the bot, which comes with Discord integration. Using this command, you may link your twitch and Discord accounts through the bot so that the same data is being tracked for you regardless of the platform on which you update it. As more commands and features are added, this will provide additional benefits.

#### `!link <twitch username>`
**Platforms**: Discord<br/>
**Aliases**: `!linkaccount`<br/>

Sends a whisper (on twitch) to the specified twitch user containing a **token** that can be used to link the two accounts. This **token** is then used in the `!linktoken` command to complete the account linking process.

---
#### `!linktoken <token>`
**Platforms**: Discord<br/>
**Must be run in a private message**

Links the twitch account specified in the `!link` command, provided that the **token** is the same one that was sent to the twitch user.  This means that to link an account, you must check your twitch whispers after sending the `!link` command and then input this token to the bot using this `!linktoken` command.

---
#### `!unlink`
**Platforms**: Twitch, Discord<br/>

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
**Must be run in a public channel**<br/>
**Moderator-only**

Opens the queue. This both allows players to challenge one another and allows moderators to add matches manually.

---
#### `!close`
**Platforms**: Twitch<br/>
**Aliases**: `!closequeue`<br/>
**Must be run in a public channel**<br/>
**Moderator-only**

Closes the queue. This prevents challenges from being issued or accepted. Moderators may no longer add matches to the queue unless they reopen it.

---
#### `!addmatch <player 1> <player 2>`
**Platforms**: Twitch<br/>
**Must be run in a public channel**<br/>
**Moderator-only**

Adds a match between the two specified players to the queue.

---
#### `!insertmatch <player 1> <player 2> <index>`
**Platforms**: Twitch<br/>
**Must be run in a public channel**<br/>
**Moderator-only**

Adds a match between the two specified players to the queue at the specified index, or at the end if the index is greater than the size of the queue.

---
#### `!movematch <start index> <end index>`
**Platforms**: Twitch<br/>
**Must be run in a public channel**<br/>
**Moderator-only**

Moves the match at the specified `start index` to the `end index`.

---
#### `!removematch <index>`<br/>
**Platforms**: Twitch<br/>
**Must be run in a public channel**<br/>
**Moderator-only**

Removes a match at the specified index from the queue.

---
#### `!clear`
**Platforms**: Twitch<br/>
**Aliases**: `!clearqueue`<br/>
**Must be run in a public channel**<br/>
**Moderator-only**

Clears the entire queue.

**NOTE**: This command must be run as `!clear yesimsure` (Yes, I'm sure) to be certain that you didn't type this command by accident.

---
#### `!winner <player> [losing score]`
**Platforms**: Twitch<br/>
**Aliases**: `!declarewinner`<br/>
**Must be run in a public channel**<br/>
**Moderator-only**

Declares the specified player the winner of a game, and stores that result (as well as the optionally provided losing score) in the current match data.

---
#### `!endmatch`
**Platforms**: Twitch<br/>
**Must be run in a public channel**<br/>
**Moderator-only**

Ends the current match, automatically determining the winner based on the match data stored each time `!winner` was called.

## Other commands

#### `!summon`
**Platforms**: Twitch, Discord

Say this in a channel the bot is in to add the bot to your Twitch channel.  If you've `!link`ed your Twitch and Discord accounts through the bot, you can even summon the bot to your Twitch channel by messaging it on Discord.

**Note**: If you plan on using the countdown command (Or if you think the bot will be chatting often), make sure you make the bot a moderator to allow it to send more than one message per second.

---
#### `!pleaseleavemychannel`
**Platforms**: Twitch<br/>
**Must be run in a private message**

Call this command in a whisper to the bot to remove the bot from your channel.

---
#### `!3`
**Platforms**: Twitch<br/>
**Moderator-only**

Counts down from 3 before saying "Tetris!" in the chat. Works for any number from 3-10. 

**Note:** If the bot is not a moderator in your Twitch channel, it will not be able to say more than one message per second, and this restriction (which is built into Twitch) will interfere with countdowns. You can make the bot a moderator by typing `/mod @ClassicTetrisBot` after you have `!summon`ed it.

---
#### `!stencil`
**Platforms**: Twitch, Discord<br/>

Prints out info on, and link to download, the (in)famous Stencil.

---
#### `!help`
**Platforms**: Twitch, Discord

Links the user to this page.

### Utility Commands

##### `!hz <level> <height> <taps>`
**Platforms**: Twitch, Discord<br/>
**Aliases**: `!hydrant`

For the given level, provides the approximate tapping speed(s) required to clear a given height with the number of taps required.

#### `!seed`
**Platforms**: Twitch, Discord<br/>
**Aliases**: `!hex`

Prints a random 6-digit hex code that is a valid NEStris seed. Used for HydrantDude's same piece sets romhack.

---
#### `!flip`
**Platforms**: Twitch, Discord<br/>
**Aliases**: `!coin`, `!coinflip`

Prints "Heads!" or "Tails!" randomly. There is no "side." The source code is available for you to verify this. Also, there is a 10 second timeout for this command to avoid spamming.

---
#### `!utc`
**Platforms**: Discord<br/>
**Aliases**: `!time`

Prints the current date and time in UTC. Used for scheduling matches with restreaamers and other players.j
