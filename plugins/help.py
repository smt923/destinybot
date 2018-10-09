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
        with open('helptext.md', 'r') as helpFile:
            contents = helpFile.read()
            event.msg.reply(contents)
