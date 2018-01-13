from threading import Thread
import time
from disco.bot import Plugin
import arrow
import dateparser


class TrialsPlugin(Plugin):
    """Disco plugin holding all of the commands related to Destiny 2 trials"""

    trialstime = arrow.get()
    istrialsset = False
    killthreads = False
    trialers = []  # this name sucks
    timer15triggered = False

    @Plugin.command('show', group='trials')
    def command_trials(self, event):
        """Show the current trials, if it is set"""
        if self.istrialsset:
            event.msg.reply("Current Trials run: {} ({})\nMembers: {}"
                            .format(arrow.get(self.trialstime).humanize(),
                                    self.trialstime.strftime(
                                        "%a, %I:%M %p %Z"),
                                    self.get_trialers_string(event)))
        else:
            event.msg.reply("No Trials set")

    @Plugin.command('new', '<rtime:str...>', group='trials')
    def command_new(self, event, rtime):
        """Set up a new trials, passing in time via argument to the bot"""
        if self.istrialsset:
            event.msg.reply('There is already a Trials run set!')
            return
        parsed = dateparser.parse(rtime, settings={'TIMEZONE': 'Europe/London',
                                                   'TO_TIMEZONE': 'Europe/London',
                                                   'RETURN_AS_TIMEZONE_AWARE': True})
        if not parsed:
            event.msg.reply('Could not detect the time, please try again')
            return
        self.trialstime = arrow.get(parsed)
        self.istrialsset = True
        self.killthreads = False
        timer_now = Thread(target=self.trialstimer_now, args=(event,))
        timer_15 = Thread(target=self.trialstimer_15, args=(event,))
        timer_now.start()
        timer_15.start()
        event.msg.reply('New Trials run: ' +
                        parsed.strftime("%A at %I:%M %p %Z"))

    @Plugin.command('edit', '<rtime:str...>', group='trials')
    def command_edit(self, event, rtime):
        """Edit the existing trials, passing in via argument to the bot"""
        if not self.istrialsset:
            event.msg.reply('There is no Trials run to edit!')
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
            timer_15 = Thread(target=self.trialstimer_15, args=(event,))
            timer_15.start()
            self.timer15triggered = False
        self.trialstime = arrow.get(parsed)
        event.msg.reply('Current Trials time changed to: ' +
                        parsed.strftime("%A at %I:%M %p %Z"))

    @Plugin.command('clear', group='trials')
    def command_clear(self, event):
        """Reset the current trials"""
        self.trials_clear(event)
        event.msg.reply('The current Trials run has been cleared')

    @Plugin.command('add', group='trials')
    def command_add(self, event):
        """Adds the user to the trials group"""
        if event.msg.author in self.trialers:
            event.msg.reply('You\'re already in the Trial, ' +
                            event.msg.author.username + '!')
            return
        self.trialers.append(event.msg.author)
        event.msg.reply('You have been added to the Trial, ' +
                        event.msg.author.username)

    @Plugin.command('remove', group='trials')
    def command_remove(self, event):
        """Removes the user from the trials group"""
        self.trialers.remove(event.msg.author)
        event.msg.reply('You have been removed from the Trial, ' +
                        event.msg.author.username)

    def trialstimer_now(self, event):
        """When there's 30 seconds left, mention the trialsgroup and reset the trials"""
        while True:
            if self.killthreads:
                break
            diff = self.trialstime - arrow.now(tz='Europe/London')
            if diff.seconds <= 30:
                trialsgroup = ""
                for members in self.trialers:
                    trialsgroup += members.mention + ", "
                event.msg.reply('Trials starting now! ' +
                                trialsgroup.rstrip(', '))
                self.trials_clear(event)
                break
            time.sleep(10)

    def trialstimer_15(self, event):
        """When there's 15 minutes left, mention the trialsgroup"""
        while True:
            if self.killthreads:
                break
            diff = self.trialstime - arrow.now(tz='Europe/London')
            minutes = diff.seconds / 60
            if minutes <= 15:
                trialsgroup = ""
                for members in self.trialers:
                    trialsgroup += members.mention + ", "
                event.msg.reply(
                    'Trials starting in 15 minutes! ' + trialsgroup.rstrip(', '))
                self.timer15triggered = True
                break
            time.sleep(30)

    def trials_clear(self, event):
        """Reset the state of trials"""
        self.trialstime = arrow.get()
        self.istrialsset = False
        self.killthreads = True
        self.timer15triggered = False
        self.trialers = []

    def get_trialers_string(self, event):
        """Gets all trial member's usernames in a single string"""
        if len(self.trialers) <= 0:
            return "None"
        trialsmembers = ""
        for member in self.trialers:
            # discord markdown for one line codeblock
            trialsmembers += "`{}` ".format(member.username)
        return trialsmembers.rstrip(' ')
