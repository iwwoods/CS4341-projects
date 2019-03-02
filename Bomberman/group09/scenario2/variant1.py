# This is necessary to find the main code
import sys
sys.path.insert(0, '../../bomberman')
sys.path.insert(1, '..')

# Import necessary stuff
from game import Game

# TODO This is your code!
sys.path.insert(1, '../group09')
from testcharacter import TestCharacter


# Create the game
g = Game.fromfile('map.txt')

# TODO Add your character
# 100:100 (100%)
active_features = [
    (1, -8.0),
    (2, 10.0),
    (5, 1.0),
    (6, -30.0),
    (7, 5.0),
    (8, 20.0),
    (9, 5.0),
    (10, 0.5),
    (11, 100.0),
]
bot = TestCharacter("me", # name
                    "C",  # avatar
                    0, 0,  # position
                    active_features,
                    0.9999,   # Decay
                    0.00  # Learning rate
)
g.add_character(bot)

# Run!
g.go(10)

# # My run
# for i in range(100):
#     g = Game.fromfile('map.txt')
#     bot.x = 0
#     bot.y = 0
#     bot.maybe_place_bomb = False
#     bot.changeState(bot.oldState1)
#     bot.state = 1
#     g.add_character(bot)
#     g.go(bot, TestCharacter.WAIT_TIME)
# print("Win ratio: " + str(bot.wins) + ":" + str(bot.wins + bot.losses))
