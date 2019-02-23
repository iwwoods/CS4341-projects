# This is necessary to find the main code
import sys
sys.path.insert(0, '../../bomberman')
sys.path.insert(1, '..')

# Import necessary stuff
import random
from game import Game
from monsters.selfpreserving_monster import SelfPreservingMonster

# TODO This is your code!
sys.path.insert(1, '../groupNN')
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

bot = TestCharacter("me", # name
                              "C",  # avatar
                              0, 0,  # position
                              [0.0, 1.0, 0.0, 0.0, 3.0, 2.0, 1.0, 0.0, 0.0],
                              0.9999,   # Decay
                              0.01  # Learning rate
)
# TODO Add your character
g.add_character(bot)

# Run!
#g.go()

# My run
for i in range(500):
    g = Game.fromfile('map.txt')
    g.add_monster(monster)
    monster.x = 3
    monster.y = 9
    g.add_character(bot)
    g.go(bot)
    bot.x = 0
    bot.y = 0
print("Win ratio: " + str(bot.wins) + ":" + str(bot.wins + bot.losses))