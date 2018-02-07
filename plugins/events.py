from threading import Thread
import time
from disco.bot import Plugin
import arrow
import dateparser
from disco.types.message import *


class RaidPlugin(Plugin):
    """Disco plugin holding all of the commands related to Destiny 2 raids"""

    raidtime = arrow.get()
    israidset = False
    killthreads = False
    raiders = []
    timer15triggered = False

    @Plugin.command('show', group='event')
    def command_raid(self, event):
        """Show the current raid, if it is set"""
        if self.israidset:
            self.eventEmbed.fields[1].value = self.get_raiders_string(event)
            self.eventEmbed.fields[0].value = self.eventTime
            # event.msg.reply("Current raid: {} ({})\nRaid members: {}"
            #.format(arrow.get(self.raidtime).humanize(),
            #self.raidtime.strftime("%a, %I:%M %p %Z"),
            # self.get_raiders_string(event)))
            event.msg.reply(embed=self.eventEmbed)
        else:
            event.msg.reply("No event set")

    @Plugin.command('new', '<rtime:str> <eventStr:str...>', group='event')
    def command_new(self, event, rtime, eventStr):
        """Set up a new raid, passing in time via argument to the bot"""
        if self.israidset:
            event.msg.reply('There is already an event set!')
            return
        parsed = dateparser.parse(rtime, settings={'TIMEZONE': 'Europe/London',
                                                   'TO_TIMEZONE': 'Europe/London',
                                                   'RETURN_AS_TIMEZONE_AWARE': True})

        savedContent = event.msg.content
        changedContent = savedContent.replace(
            '<@378562216133394434> event new ', "")
        timeInfoEnd = changedContent.find(" ")

        eventStr = changedContent[timeInfoEnd + 1:1000000]
        eventParts = ""

        if '|' in eventStr:
            eventParts = eventStr.split('|')
        elif '~' in eventStr:
            eventParts = eventStr.split('~')
        elif '-' in eventStr:
            eventParts = eventStr.split('-')

        eventTitle = eventParts[0]
        eventDesc = eventParts[1]

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

        #event.msg.reply('Event Created! {0}: '.format(eventTitle) + parsed.strftime("%A at %I:%M %p %Z"))

        self.eventEmbed = MessageEmbed(
            title=eventTitle, description=eventDesc, color=3447003)

        self.eventTime = parsed.strftime("%A at %I:%M %p %Z")
        self.eventTitle = eventTitle

        self.eventEmbed.add_field(
            name="Time", value=self.eventTime, inline=False)
        # save all this stuff as a attribute of the plugin so we can access it in 'show' and other functions
        self.eventEmbed.add_field(
            name="Members", value=self.get_raiders_string(event), inline=False)

        #message = Message(embeds=list(embed))

        event.msg.reply(embed=self.eventEmbed)

    @Plugin.command('edit', '<rtime:str...>', group='event')
    def command_edit(self, event, rtime):
        """Edit the existing raid, passing in via argument to the bot"""
        if not self.israidset:
            event.msg.reply('There is no event to edit!')
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
        self.eventTime = parsed.strftime("%A at %I:%M %p %Z")
        event.msg.reply('Current event time changed to: ' +
                        parsed.strftime("%A at %I:%M %p %Z"))

    @Plugin.command('clear', group='event')
    def command_clear(self, event):
        """Reset the current raid"""
        self.raid_clear(event)
        event.msg.reply('The current event has been cleared')

    @Plugin.command('add', group='event')
    def command_add(self, event):
        """Adds the user to the raid group"""
        if event.msg.author in self.raiders:
            event.msg.reply('You\'re already in the event, ' +
                            event.msg.author.username + '!')
            return
        self.raiders.append(event.msg.author)
        event.msg.reply('You have joined the event, ' +
                        event.msg.author.username)

    @Plugin.command('remove', group='event')
    def command_remove(self, event):
        """Removes the user from the raid group"""
        self.raiders.remove(event.msg.author)
        event.msg.reply('You have been removed from the event, ' +
                        event.msg.author.username)

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
                #raidstartEmbed = MessageEmbed(title=self.eventEmbed.title + "starting now!", description=raidgroup.rstrip(', '))
                event.msg.reply('{} starting now! '.format(
                    self.eventEmbed.title.rstrip(' ')) + raidgroup.rstrip(', '))
                # event.msg.reply(embed=raidstartEmbed)
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
                event.msg.reply(
                    'Event starting in 15 minutes! ' + raidgroup.rstrip(', '))
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

    def get_random_teams(self, event):
        pass

    def start_draft(self, event):
        pass
