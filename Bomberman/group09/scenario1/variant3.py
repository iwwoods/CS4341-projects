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
monster = SelfPreservingMonster("selfpreserving", # name
                                    "S",              # avatar
                                    3, 9,             # position
                                    1                 # detection range
)
g.add_monster(monster)

# 85:100 (85%)
'''
active_features = [
    (6, -3580.1215088319373),
    (8, 1177.6500689014392)
]
'''
# 87:100 (87%)
'''
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
'''

# 84:99 (84.84848484848484%)
'''
active_features = [
    (2, 10.0),
    (5, 1.0),
    (6, -30.0),
    (7, 5.0),
    (8, 20.0),
    (9, 5.0),
    (10, 0.5),
    (11, 100.0),
]
'''

# 93:99 (93.93939393939394%)
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
                    #[0.0, 0.0, 0.0, 0.0, 0.0, -1000.0, 0.0, 1200.0, 0.0, 0.0, 0.0],
                    active_features,
                    #[0.0, 0.0, 0.0, 0.0, 0.0, -7372.384172244952, 2423.2029157617908, 0.0, 0.0, 0.0, 0.0], # 90%
                    #[0.0, 0.0, 0.0, 0.0, 0.0, -13603.865562562338, 3707.3437077483977, 0.0, 0.0, 0.0, 0.0], # 88%
                    #[0.0, 0.0, 0.0, 0.0, 0.0, -23631.89743163873, 6748.757318256902, 0.0, 0.0, 0.0, 0.0], # 90%
                    0.9999,   # Decay
                    0.00  # Learning rate
)
bot.alt7 = True
# TODO Add your character
g.add_character(bot)

# Run!
g.go(10)


# # My run
# for i in range(99):
#     g = Game.fromfile('map.txt')
#     monster.x = 3
#     monster.y = 9
#     g.add_monster(monster)
#     bot.x = 0
#     bot.y = 0
#     bot.maybe_place_bomb = False
#     bot.changeState(bot.oldState1)
#     bot.state = 1
#     g.add_character(bot)
#     g.go(bot, TestCharacter.WAIT_TIME)
# print("Win ratio: " + str(bot.wins) + ":" + str(bot.wins + bot.losses))