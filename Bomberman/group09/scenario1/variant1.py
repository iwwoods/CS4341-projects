# This is necessary to find the main code
import sys
sys.path.insert(0, '../../bomberman')
sys.path.insert(1, '..')

# Import necessary stuff
from game import Game

# TODO This is your code!
sys.path.insert(1, '../groupNN')
from testcharacter import TestCharacter


# Create the game
g = Game.fromfile('map.txt')

# TODO Add your character
bot = TestCharacter("me", # name
                    "C",  # avatar
                    0, 0, # position
                    [0.0, 0.0, 0.0, 0.0, 0.0, 10.0, 0.0],
                    0.9999, # Decay
                    0.01  # Learning rate
)
g.add_character(bot)

# Run!
#g.go(bot)

# My run
for i in range(100):
    g = Game.fromfile('map.txt')
    g.add_character(bot)
    g.go(bot)
    bot.x = 0
    bot.y = 0
print("Win ratio: " + str(bot.wins) + ":" + str(bot.wins + bot.losses))
