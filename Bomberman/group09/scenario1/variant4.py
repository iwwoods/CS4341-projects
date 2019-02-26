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

monster = SelfPreservingMonster("monster", # name
                                    "M",       # avatar
                                    3, 13,     # position
                                    2          # detection range
)
g.add_monster(monster)

active_features = [
    (1, 1.0),
    (4, 1.0),
    (5, -30.0),
    (7, 20.0),
    (8, -5.0),
    (9, 0.5),
]
bot = TestCharacter("me", # name
                    "C",  # avatar
                    0, 0,  # position
                    active_features,
                    0.9999,   # Decay
                    0.001  # Learning rate
)
# TODO Add your character
g.add_character(bot)

# Run!
#g.go()

# My run
for i in range(100):
    g = Game.fromfile('map.txt')
    monster.x = 3
    monster.y = 9
    g.add_monster(monster)
    bot.x = 0
    bot.y = 0
    bot.maybe_place_bomb = False
    bot.changeState(bot.oldState1)
    bot.state = 1
    g.add_character(bot)
    g.go(bot, TestCharacter.WAIT_TIME)
print("Win ratio: " + str(bot.wins) + ":" + str(bot.wins + bot.losses))