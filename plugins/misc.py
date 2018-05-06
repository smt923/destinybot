from disco.bot import Plugin
import random

class MiscPlugin(Plugin):
    """random stuff there's no other place for"""

    fortnite_locations = ["Junk Junction", "Haunted Hills", "Pleasant Park", "Loot Lake", "Anarchy Acres", "Risky Reels", "Wailing Woods",
                          "Tomato Town", "Lonely Lodge", "Snobby Shores", "Tilted Towers", "Dusty Divot", "Retail Row", "Greasy Grove",
                          "Shifty Shafts", "Salty Springs", "Flush Factory", "Fatal Fields", "Moisty Mire", "Lucky Landing", "Prison"]

    @Plugin.command('drop')
    def select_drop(self, event): #possible to expand for other games if we decide to
        randomInt = random.randint(0, (len(self.fortnite_locations) - 1))

        selected_location = self.fortnite_locations[randomInt]

        event.msg.reply("Where we dropping boys?! **{}!**".format(selected_location))

