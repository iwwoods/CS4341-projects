# This is necessary to find the main code
import sys
sys.path.insert(0, '../../bomberman')
sys.path.insert(1, '..')

# Import necessary stuff
import random
from game import Game
from monsters.stupid_monster import StupidMonster
from monsters.selfpreserving_monster import SelfPreservingMonster

# TODO This is your code!
sys.path.insert(1, '../groupNN')
from testcharacter import TestCharacter

# Create the game
random.seed(123) # TODO Change this if you want different random choices
g = Game.fromfile('map.txt')
monster1 = StupidMonster("monster", # name
                            "S",       # avatar
                            3, 5,      # position
)
g.add_monster(monster1)
monster2 = SelfPreservingMonster("monster", # name
                                    "A",       # avatar
                                    3, 13,     # position
                                    2          # detection range
)
g.add_monster(monster2)

# TODO Add your character
bot = TestCharacter("me", # name
                              "C",  # avatar
                              0, 0,  # position
                              [0.0, 1.0, 0.0, 0.0, 1.0, -30.0, 0.0, 20.0, -5.0, 0.5, 40.0],
                              0.9999,   # Decay
                              0.001  # Learning rate
)
g.add_character(bot)

# Run!
#g.go()

# My run
for i in range(100):
    g = Game.fromfile('map.txt')
    monster1.x = 3
    monster1.y = 5
    g.add_monster(monster1)
    monster2.x = 3
    monster2.y = 13
    g.add_monster(monster2)
    bot.x = 0
    bot.y = 0
    bot.maybe_place_bomb = False
    bot.changeState(bot.oldState1)
    bot.state = 1
    g.add_character(bot)
    g.go(bot)
print("Win ratio: " + str(bot.wins) + ":" + str(bot.wins + bot.losses))