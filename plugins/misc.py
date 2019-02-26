from disco.bot import Plugin
from disco.util.sanitize import S

import random

class MiscPlugin(Plugin):
    """random stuff there's no other place for"""

    fortnite_locations = ["Junk Junction", "Haunted Hills", "Pleasant Park", "Loot Lake", "Anarchy Acres", "Risky Reels", "Wailing Woods",
                          "Tomato Town", "Lonely Lodge", "Snobby Shores", "Tilted Towers", "Dusty Divot", "Retail Row", "Greasy Grove",
                          "Shifty Shafts", "Salty Springs", "Flush Factory", "Fatal Fields", "Moisty Mire", "Lucky Landing", "Prison"]

    apex_locations = ["Slum Lakes", "Artillery", "Relay", "The Pit", "Cascades", "Wetlands", "Runoff", "Bunker", "Swamps", "Airbase", 
                      "Bridges", "Hydro Dam", "Market", "Skull Town", "Repulsor", "Thunderdome", "Water Treatment", "Hot Zone", "Supply Ship"]

    @Plugin.command('fortnite', group='drop')
    def select_drop(self, event): #possible to expand for other games if we decide to
        randomInt = random.randint(0, (len(self.fortnite_locations) - 1))

        selected_location = self.fortnite_locations[randomInt]
        
        event.msg.reply("[Fortnite] Where we dropping boys?! **{}!**".format(selected_location))

    @Plugin.command('apex', group='drop')
    def select_drop_apex(self, event): #possible to expand for other games if we decide to
        randomInt = random.randint(0, (len(self.apex_locations) - 1))

        selected_location = self.apex_locations[randomInt]

        event.msg.reply("[Apex] Where we dropping boys?! **{}!**".format(selected_location))


    @Plugin.command('roll', parser=True)
    @Plugin.parser.add_argument('dice_range', type=int, nargs=1)
    @Plugin.parser.add_argument('custom_message', type=str, nargs='*')
    def roll_custom_die(self, event, args):
        if args.dice_range[0] <= 0:
            event.msg.reply("Please roll a dice with a positive number")
            return
            
        randomInt = random.randint(1, args.dice_range[0])
        
        message_string = "!"
        if len(args.custom_message) > 0:
            message_string = " for **"
            for each in args.custom_message:
                message_string += each
                message_string += " "
            message_string += "**"
        else:
            pass

        event.msg.reply("Rolling a ``d{0}``{1} \nRolled **``{2}``**!".format(args.dice_range[0], message_string, randomInt))


    @Plugin.command('flip', parser=True)
    @Plugin.parser.add_argument('custom_message', type=str, nargs='*')
    def flip_coin(self, event, args):

        randomInt = random.randint(0, 1)

        print(randomInt)

        if not randomInt:
            coinResult = "Heads"
        else:
            coinResult = "Tails"

        message_string = ""
        if len(args.custom_message) > 0:
            message_string = "**"
            for each in args.custom_message:
                message_string += each
                message_string += " "
            message_string += "**"
        else:
            pass

        event.msg.reply("Flipping a Coin! {0}\n**``{1}!``**".format(message_string, coinResult))

