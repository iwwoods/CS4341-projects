# This is necessary to find the main code
import sys
sys.path.insert(0, '../../bomberman')
sys.path.insert(1, '..')

# Import necessary stuff
import random
from game import Game
from monsters.selfpreserving_monster import SelfPreservingMonster

# TODO This is your code!
sys.path.insert(1, '../group09')
from testcharacter import TestCharacter

# Create the game
random.seed(123) # TODO Change this if you want different random choices
g = Game.fromfile('map.txt')
monster = SelfPreservingMonster("aggressive", # name
                                    "A",          # avatar
                                    3, 13,        # position
                                    2             # detection range
)
g.add_monster(monster)

# TODO Add your character
# 96:100 (96%)
active_features = [
    (1, -7),
    (2, 10.0),
    (5, 1.0),
    (6, -30.0),
    (7, 5.0),
    (8, 21.0),
    (9, 7.0),
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
#g.go(bot, wait=1)

# My run

for i in range(100):
    g = Game.fromfile('map.txt')
    monster.x = 3
    monster.y = 13
    g.add_monster(monster)
    bot.x = 0
    bot.y = 0
    bot.maybe_place_bomb = False
    bot.changeState(bot.oldState1)
    bot.state = 1
    g.add_character(bot)
    g.go(bot, TestCharacter.WAIT_TIME)
print("Win ratio: " + str(bot.wins) + ":" + str(bot.wins + bot.losses))
