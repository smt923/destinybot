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
        event.msg.reply("All commands must be sent by mentioning me:\n**Type Raid or Trials before these**\n{}\n{}\n{}\n{}\n{}\n{}\n**Map**\n{}\n{}\n{}\n{}"
                        .format("`new <time>` - set a new raid/trial with a given time (eg, 10pm)",
                                "`edit <time>` - edit the current raid/trial with a new time",
                                "`clear` - clear the currently set raid/trial",
                                "`show` - show the current raid/trial, if any",
                                "`add` - add yourself to the current raid/trial",
                                "`remove` - remove yourself from the current raid/trial",
                                "`map underbelly` - post the map of the leviathan underbelly",
                                "`map underbelly3d` - post the 3D map of the leviathan underbelly",
                                "`map doggos` - post the map of the Pleasure Gardens raid room",
                                "`map voidcall` - post a chart of the four symbols found in raids"))
