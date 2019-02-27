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
g.go(bot, wait=1)
