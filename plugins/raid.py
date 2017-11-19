from threading import Thread
import time
from disco.bot import Plugin
import arrow
import dateparser

class RaidPlugin(Plugin):
    """Disco plugin holding all of the commands related to Destiny 2 raids"""

    raidtime = arrow.get()
    israidset = False
    killthreads = False
    raiders = []
    timer15triggered = False

    @Plugin.command('help')
    def command_help(self, event):
        """Help for all commands"""
        # todo: tidy this messy format string somehow - make it it's own disco plugin and have each
        # individual plugin generate it's own help from it's commands?
        event.msg.reply("All commands must be sent by mentioning me:\n**Raid**\n{}\n{}\n{}\n{}\n{}\n{}\n**Map**\n{}\n{}\n{}"
                        .format("`raid new <time>` - set a new raid with a given time (eg, 10pm)",
                                "`raid edit <time>` - edit the current raid with a new time",
                                "`raid clear` - clear the currently set raid",
                                "`raid show` - show the current raid, if any",
                                "`raid add` - add yourself to the current raid",
                                "`raid remove` - remove yourself from the current raid",
                                "`map underbelly` - post the map of the leviathan underbelly",
                                "`map underbelly3d` - post the 3D map of the leviathan underbelly",
                                "`map doggos` - post the map of the Pleasure Gardens raid room"))

    @Plugin.command('show', group='raid')
    def command_raid(self, event):
        """Show the current raid, if it is set"""
        if self.israidset:
            event.msg.reply("Current raid: {} ({})\nRaid members: {}"
                            .format(arrow.get(self.raidtime).humanize(),
                                    self.raidtime.strftime("%a, %I:%M %p %Z"),
                                    self.get_raiders_string(event)))
        else:
            event.msg.reply("No raid set")

    @Plugin.command('new', '<rtime:str...>', group='raid')
    def command_new(self, event, rtime):
        """Set up a new raid, passing in time via argument to the bot"""
        if self.israidset:
            event.msg.reply('There is already a raid set!')
            return
        parsed = dateparser.parse(rtime, settings={'TIMEZONE': 'Europe/London',
                                                   'TO_TIMEZONE': 'Europe/London',
                                                   'RETURN_AS_TIMEZONE_AWARE': True})
        if not parsed:
            event.msg.reply('Could not detect the time, please try again')
            return
        self.raidtime = arrow.get(parsed)
        self.israidset = True
        self.killthreads = False
        timer_now = Thread(target=self.raidtimer_now, args=(event,))
        timer_15 = Thread(target=self.raidtimer_15, args=(event,))
        timer_now.start()
        timer_15.start()
        event.msg.reply('New raid: ' + parsed.strftime("%A at %I:%M %p %Z"))

    @Plugin.command('edit', '<rtime:str...>', group='raid')
    def command_edit(self, event, rtime):
        """Edit the existing raid, passing in via argument to the bot"""
        if not self.israidset:
            event.msg.reply('There is no raid to edit!')
            return
        parsed = dateparser.parse(rtime, settings={'TIMEZONE': 'Europe/London',
                                                   'TO_TIMEZONE': 'Europe/London',
                                                   'RETURN_AS_TIMEZONE_AWARE': True})
        if not parsed:
            event.msg.reply('Could not detect the time, please try again')
            return
        diff = arrow.get(parsed) - arrow.now(tz='Europe/London')
        # if the 15 minute timer triggered, and there's more than 15 minutes left, restart it
        if self.timer15triggered and diff.seconds / 60 > 15:
            timer_15 = Thread(target=self.raidtimer_15, args=(event,))
            timer_15.start()
            self.timer15triggered = False
        self.raidtime = arrow.get(parsed)
        event.msg.reply('Current raid time changed to: ' + parsed.strftime("%A at %I:%M %p %Z"))

    @Plugin.command('clear', group='raid')
    def command_clear(self, event):
        """Reset the current raid"""
        self.raid_clear(event)
        event.msg.reply('The current raid has been cleared')

    @Plugin.command('add', group='raid')
    def command_add(self, event):
        """Adds the user to the raid group"""
        if event.msg.author in self.raiders:
            event.msg.reply('You\'re already in the raid, ' + event.msg.author.username + '!')
            return
        self.raiders.append(event.msg.author)
        event.msg.reply('You have been added to the raid, ' + event.msg.author.username)

    @Plugin.command('remove', group='raid')
    def command_remove(self, event):
        """Removes the user from the raid group"""
        self.raiders.remove(event.msg.author)
        event.msg.reply('You have been removed from the raid, ' + event.msg.author.username)

    def raidtimer_now(self, event):
        """When there's 30 seconds left, mention the raidgroup and reset the raid"""
        while True:
            if self.killthreads:
                break
            diff = self.raidtime - arrow.now(tz='Europe/London')
            if diff.seconds <= 30:
                raidgroup = ""
                for members in self.raiders:
                    raidgroup += members.mention + ", "
                event.msg.reply('Raid starting now! ' + raidgroup.rstrip(', '))
                self.raid_clear(event)
                break
            time.sleep(10)

    def raidtimer_15(self, event):
        """When there's 15 minutes left, mention the raidgroup"""
        while True:
            if self.killthreads:
                break
            diff = self.raidtime - arrow.now(tz='Europe/London')
            minutes = diff.seconds / 60
            if minutes <= 15:
                raidgroup = ""
                for members in self.raiders:
                    raidgroup += members.mention + ", "
                event.msg.reply('Raid starting in 15 minutes! ' + raidgroup.rstrip(', '))
                self.timer15triggered = True
                break
            time.sleep(30)

    def raid_clear(self, event):
        """Reset the state of raid"""
        self.raidtime = arrow.get()
        self.israidset = False
        self.killthreads = True
        self.timer15triggered = False
        self.raiders = []

    def get_raiders_string(self, event):
        """Gets all raid member's usernames in a single string"""
        if len(self.raiders) <= 0:
            return "None"
        raidmembers = ""
        for member in self.raiders:
            # discord markdown for one line codeblock
            raidmembers += "`{}` ".format(member.username)
        return raidmembers.rstrip(' ')
