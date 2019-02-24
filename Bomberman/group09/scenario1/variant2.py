# This is necessary to find the main code
import sys
sys.path.insert(0, '../../bomberman')
sys.path.insert(1, '..')

# Import necessary stuff
import random
from game import Game
from monsters.stupid_monster import StupidMonster

# TODO This is your code!
sys.path.insert(1, '../groupNN')
from testcharacter import TestCharacter

# Create the game
random.seed(123) # TODO Change this if you want different random choices
g = Game.fromfile('map.txt')

monster = StupidMonster("monster", # name
                            "M",       # avatar
                            3, 9       # position
)
g.add_monster(monster)

bot = TestCharacter("me", # name
                              "C",  # avatar
                              0, 0,  # position
                              [0.0, 0.0, 0.0, 0.0, 0.0, -3036.43566109191, 874.8232805447983, 0.0, 0.0, 0.0, 0.0], # 98%
                              #[0.0, 0.0, 0.0, 0.0, 0.0, -6136.43566109191, 874.8232805447983, 0.0, 0.0, 0.0, 0.0], # 95%
                              #[0.0, 0.0, 0.0, 0.0, 0.0, -10.0, 10.0, 0.0, 0.0, 0.0, 0.0],
                              0.9999,   # Decay
                              0.00  # Learning rate
)
# TODO Add your character
g.add_character(bot)

# Run!
#g.go(bot)

# My run
for i in range(100):
    g = Game.fromfile('map.txt')
    monster.x = 3
    monster.y = 9
    g.add_monster(monster)
    bot.x = 0
    bot.y = 0
    bot.changeState(bot.oldState1)
    bot.state = 1
    g.add_character(bot)
    g.go(bot)
print("Win ratio: " + str(bot.wins) + ":" + str(bot.wins + bot.losses))