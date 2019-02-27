# This is necessary to find the main code
import sys
sys.path.insert(0, '../../bomberman')
sys.path.insert(1, '..')

# Import necessary stuff
import random
from game import Game
from monsters.stupid_monster import StupidMonster

# TODO This is your code!
sys.path.insert(1, '../group09')
from testcharacter import TestCharacter

# Create the game
random.seed(123) # TODO Change this if you want different random choices
g = Game.fromfile('map.txt')
monster = StupidMonster("stupid", # name
                            "S",      # avatar
                            3, 9      # position
)
g.add_monster(monster)

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
#g.go(bot, wait=1)

# My run

for i in range(10):
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
