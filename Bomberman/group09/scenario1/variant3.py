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
                                    3, 9,      # position
                                    1          # detection range
)
g.add_monster(monster)

bot = TestCharacter("me", # name
                              "C",  # avatar
                              0, 0,  # position
                              #[0.0, 0.0, 0.0, 0.0, 0.0, -1000.0, 0.0, 1200.0, 0.0, 0.0],
                              [0.0, 0.0, 0.0, 0.0, 0.0, -3580.1215088319373, 0.0, 1177.6500689014392, 0.0, 0.0],
                              #[0.0, 0.0, 0.0, 0.0, 0.0, -7372.384172244952, 2423.2029157617908, 0.0, 0.0, 0.0], # 90%
                              #[0.0, 0.0, 0.0, 0.0, 0.0, -13603.865562562338, 3707.3437077483977, 0.0, 0.0, 0.0], # 88%
                              #[0.0, 0.0, 0.0, 0.0, 0.0, -23631.89743163873, 6748.757318256902, 0.0, 0.0, 0.0], # 90%
                              0.9999,   # Decay
                              0.00  # Learning rate
)
bot.alt7 = True
# TODO Add your character
g.add_character(bot)

# Run!
#g.go()


# My run
for i in range(99):
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