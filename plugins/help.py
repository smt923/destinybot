from disco.bot import Plugin


class HelpPlugin(Plugin):
    @Plugin.listen('Ready')
    def on_ready(self, event):
        """Ready event - prints the url to connect the bot to a guild"""
        print('Connected as {}'
              .format(event.user.username))
        print('Invite URL: https://discordapp.com/oauth2/authorize?client_id={}&scope=bot'
              .format(event.user.id))

    @Plugin.command('help')
    def command_help(self, event):
        """Help for all commands"""
        # todo: tidy this messy format string somehow - have each
        # plugin generate it's own help?
        event.msg.reply("All commands must be sent by mentioning me:\n**Event**\n{}\n{}\n{}\n{}\n{}\n{}\n**Map**\n{}\n{}\n{}\n{}\n{}\n{}"
                        .format("`new <time> <Event Title> ~ <Event Description>` - set a new event with a given time (eg, 10pm). Split event title and description with a |, - or ~ character!",
                                "`edit <time>` - edit the current event with a new time",
                                "`clear` - clear the currently set event",
                                "`show` - show the current event, if any",
                                "`add` - add yourself to the current event",
                                "`remove` - remove yourself from the current event",
                                "`map underbelly` - post the map of the leviathan underbelly",
                                "`map underbelly3d` - post the 3D map of the leviathan underbelly",
                                "`map doggos` - post the map of the Pleasure Gardens raid room",
                                "`map pdoggos` - post the map of the prestige Pleasure Gardens raid room",
                                "`map voidcall` - post a chart of the four symbols found in raids",
                                "`map pbathers` - post a map of the prestige bathhouse callouts"))
