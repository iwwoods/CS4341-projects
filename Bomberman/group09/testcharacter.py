# This is necessary to find the main code
import sys
sys.path.insert(0, '../bomberman')
# Import necessary stuff
from entity import CharacterEntity
from sensed_world import SensedWorld
from monsters.selfpreserving_monster import SelfPreservingMonster
from colorama import Fore, Back
import random
import math
from queue import PriorityQueue
from functools import reduce


'''
 To add feature:
   Update NUM_FEATURES
   Add to calcFeatureN function
   - Add function to calculate feature
'''

# feature0 Dummy feature to represent bias
# feature1 Manhattan distance to door
# feature2 Manhattan distance to bomb in col/row
# feature3 number of neighboring walls
# feature4 distance from closest side wall
# feature5 number bombs on the field
# feature6 A*
# feature7 Closest enemy
# feature8 Closest enemy in range of 3
# feature9 Corner detection
# feature10 Enemy in range 6 manhattan distance
# feature11 Enemy in detection

# Potential uses for bombs: find goal, destroy walls (most walls, walls that corner you), kill enemy/other players
#TODO: Add features to dictate bomb placement (ex. postive reward for holding on to a bomb so it only places when the placement is high enough value)

#TODO: Performs an action after end?
#TODO: Fix feature 11
#TODO: Address potential action after death in calcQ

#TODO: When enemy lockes on its pretty much impossible to not die, Find a way around this, maybe look at enemy's code and find what causes lock on
#TODO: Does the bomb trigger when the enemy steps on it? or when we do? maybe add feature valuing holding onto a bomb for the right moment?
#TODO: Optimize main function (some features are repetitive... consolidate? (ex find closest enemy first then pass in))
#TODO: Ensure code all works when door isnt visible
#TODO: Add state change for when door is visible or not
#TODO: Add feature 12, number of walls inside range n (n = bomb range)


class TestCharacter(CharacterEntity):
    NUM_FEATURES = 12
    WAIT_TIME = 50

    def __init__(self, name, avatar, x, y, active_features, decay, lr):
        CharacterEntity.__init__(self, name, avatar, x, y)
        # Weights turned on (if 0 in 6th spot 6th feature turned off)
        self.on = [0.0] * self.NUM_FEATURES
        for feat_num, weight in active_features:
            self.on[feat_num] = weight

        self.weightArray = self.on # Array of weights
        self.featureArray = [0.0] * self.NUM_FEATURES # Array of features
        self.gamma = 0.9        # Reward Decay
        self.lr = lr            # Learning Rate
        self.decay = decay      # Decay
        self.wins = 0           # Number of wins so far
        self.losses = 0         # Number of losses so far
        self.debug = True       # Turn off to reduce prints
        self.oldState1 = self.on     # Used to save a state to revert back to later
        self.oldState2 = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, -5.0, 0.0, 0.0, 0.0, 0.0, 0.0]     # Used to save a state to revert back to later (go directly towards goal state)
        self.state = 1          # State the bot is currently in

        self.monster_aggro_range = 2

    # Execute action for this turn
    def do(self, wrld):
        # Your code here
        validMoves = self.calcVMoves(wrld)  # Find all valid moves
        move = random.randint(0,len(validMoves)-1)  # Randomly pick move

        # Interactive
        hMove = -1
        move = -1
        print(validMoves)
        #hMove = int(input("Pick a move"))
        #print(hMove)

        # Learning
        qMove = -1
        if(True):  #self.lr == 0.0 or random.randint(0, 5) != 0):  # Add some randomness
            self.printFeatures()
            maxQ = None
            for m in range(len(validMoves)):
                moveQVal = self.calcQ(wrld, validMoves[m])
                if maxQ is None or moveQVal > maxQ:
                    qMove = validMoves[m]
                    maxQ = moveQVal
                if self.debug:
                    print(str(validMoves[m]) + ": " + str(moveQVal))
            if self.debug:
                print("Q Move: " + str(qMove))
        else:
            if self.debug:
                print("Random move: " + str(validMoves[move]))

        if hMove in validMoves:
            self.makeMove(hMove)
        elif qMove in validMoves:
            self.makeMove(qMove)
        elif move < len(validMoves):
            self.makeMove(validMoves[move])
        else:
            print("Invalid Move")
            pass

    # Calculate Q value for state and action
    # action = -1 means no action, eval current state
    def calcQ(self, wrld, action):
        sx = self.x
        sy = self.y
        world = wrld

        is_global = False
        if action == -1:
            is_global = True
        else:   # Only do if action taken/ time passed
            sim_world = SensedWorld.from_world(wrld)  # Create copy of world to run simulation on
            myself = sim_world.me(self)               # Find my character in the simulated world (this is a copy of first char so technically different)
            #if myself is None:  #TODO: Find way to handle gameover, myself is None
            self.makeMove(action, myself)             # Execute action
            new_state = sim_world.next()              # Simulate outcome (returns (new_world, events))
            sim_world = new_state[0]
            myself = sim_world.me(self)               # Update my character from new world
            if myself is not None:
                sx = myself.x
                sy = myself.y
            if myself is None:
                return self.calcReward(new_state[1], 0)
            world = new_state[0]

        featureArray = [0.0] * self.NUM_FEATURES

        for i, is_on in enumerate(self.on):
            featureArray[i] = 0.0
            if is_on:
                featureVal = self.calcFeatureN(i, world, action, sx, sy, is_global, wrld)

                if is_global:
                    self.featureArray[i] = featureVal
                else:
                    featureArray[i] = featureVal

        # Change state under certain conditions
        if action == -1 and self.state == 1:
            enemyDist = None
            goalDist = 0

            # Fill goalDist
            if (self.on[6] != 0):
                goalDist = self.featureArray[6]
            else:
                goalDist = self.calcFeature6(world, action, sx, sy)

            # Fill enemyDist (enemy to door)
            for e in world.monsters:
                astar = self.aStar(world, world.exitcell, world.monsters[e][0].x, world.monsters[e][0].y)
                if astar == -1:
                    continue
                if enemyDist is None:
                    enemyDist = len(astar)
                else:
                    dist = len(astar)
                    if dist != 0:
                        enemyDist = min(enemyDist, dist)

            if enemyDist is not None:
                if enemyDist > 0:
                    largestDim = max(world.height(), world.width())
                    # enemyDist = enemyDist -1 # Monster moves first (sim = monster move, our move, pause)
                    enemyDist = math.sqrt(enemyDist) / math.sqrt(largestDim * 4)
                enemyDist = self.renorm(enemyDist)

            # If a monster is blocked off from the exit character may run towards the exit when the monster may only be
            # temporarily blocked (maybe add a temporary check?) ex.
            '''
            +--------+
            |   A*  C|
            |    * @ |
            |********|
            | W W*   |
            |    *   |
            |    *   |
            |    * S |
            |    WWWW|
            |        |
            |        |
            |        |
            |WWWW    |
            |        |
            |        |
            |        |
            |    WWWW|
            |        |
            |        |
            |       #|
            +--------+
            '''
            if enemyDist is None or goalDist < enemyDist:
                self.saveOldState(self.state)
                self.changeState(self.oldState2)  # Go straight to goal
                self.state = 2

        # Compute the Q val from weights and features
        if (is_global):
            # if self.debug:
                # self.printFeatures()
            return reduce(lambda prev, weight_feature_pair: prev + weight_feature_pair[0] * weight_feature_pair[1],
                          zip(self.weightArray, self.featureArray), 0)
        else:
            if self.debug:
                print("Features: " + str(featureArray))
            return reduce(lambda prev, weight_feature_pair: prev + weight_feature_pair[0] * weight_feature_pair[1],
                          zip(self.weightArray, featureArray), 0)

    #####################
    # Feature Calculation
    #####################

    # Calculate a given feature
    def calcFeatureN(self, n, world, action, sx, sy, is_global, oldworld):
        # Enemy detection range
        if n == 11:
            return self.calcFeature11(world, action, sx, sy)

        # Closest enemy in range of 6
        if n == 10:
            return self.calcFeature10(world, action, sx, sy)

        # Corner detection
        if n == 9:
            return self.calcFeature9(world, action, sx, sy)

        # Closest enemy in range of 3
        if n == 8:
            return self.calcFeature8(world, action, sx, sy)

        # Enemy dist
        if n == 7:
            return self.calcFeature7(world, action, sx, sy)

        # A*
        if n == 6:
            return self.calcFeature6(world, action, sx, sy)

        # Bombs on the field
        if n == 5:
            return self.calcFeature5(world, action, sx, sy)

        # Dist from side walls
        if n == 4:
            return self.calcFeature4(world, action, sx, sy)

        # neighboring walls
        if n == 3:
            return self.calcFeature3(world, action, sx, sy)

        # bomb dist on lines calc
        if n == 2:
            return self.calcFeature2(world, action, sx, sy)

        # Manhattan dist calc
        if n == 1:
            return self.calcFeature1(world, action, sx, sy)

        # Dummy feature
        if n == 0:
            return 1

    # Calculate feature 1 value for state and action
    def calcFeature1(self, wrld, action, sx, sy):
        # Manhattan dist calc
        exitVisable = wrld.exitcell != None
        distToExit = wrld.height()  # Large value
        if exitVisable:
            distToExit = self.calcMDist(sx, sy, wrld.exitcell[0], wrld.exitcell[1])
        feature1 = distToExit/(wrld.width() + wrld.height())
        feature1 = self.renorm(feature1)

        return feature1

    # Calculate feature 2 value for state and action
    def calcFeature2(self, wrld, action, sx, sy):
        # bomb dist on lines calc
        ''' OLD DIST CODE
        largestDim = max(wrld.height(), wrld.width())
        feature2 = largestDim/largestDim
        if action == 1 or self.is_bomb_at(wrld, sx, sy):
            feature2 = 0/largestDim
        for k in wrld.bombs:
            if wrld.bombs[k].x == sx:
                feature2 = min(feature2, abs(wrld.bombs[k].y - sy)+wrld.bomb_time/largestDim+9)
            if wrld.bombs[k].y == sy:
                feature2 = min(feature2, abs(wrld.bombs[k].x - sx)+wrld.bomb_time/largestDim+9)
        feature2 = self.renorm(feature2)
        '''

        # find if bomb is in range
        range = wrld.expl_range
        ticksToIgnore = 7  # ignores bomb positioning for first four seconds to allow free movement
        feature2 = wrld.bomb_time-ticksToIgnore
        for k in wrld.bombs:
            if wrld.bombs[k].x == sx:
                if abs(wrld.bombs[k].y - sy) <= range:
                    feature2 = min(feature2, wrld.bombs[k].timer)
            if wrld.bombs[k].y == sy:
                if abs(wrld.bombs[k].x - sx) <= range:
                    feature2 = min(feature2, wrld.bombs[k].timer)
        feature2 = self.renorm(feature2/(wrld.bomb_time-ticksToIgnore))
        return feature2

    # Calculate feature 3 value for state and action
    def calcFeature3(self, wrld, action, sx, sy):
        feature3 = self.renorm(self.surroundingWallCount(wrld, (sx, sy))/8)
        return feature3

    # Calculate feature 4 value for state and action
    def calcFeature4(self, wrld, action, sx, sy):
        #feature4 = self.renorm(min(sx, wrld.width()-sx)/(wrld.width()/2))
        minDist = min(sx, wrld.width()-sx)/(wrld.width()/2)
        feature4 = 1
        i = 0
        while i < minDist:
            feature4 = feature4/2
            i += 1
        return self.renorm(feature4)

    # Calculate feature 5 value for state and action
    def calcFeature5(self, wrld, action, sx, sy):
        value = 1.0
        for b in wrld.bombs:
            value = 0.0
        value = self.renorm(value)
        return -value

    # Calculate feature 6 value for state and action
    def calcFeature6(self, wrld, action, sx, sy):
        largestDim = max(wrld.height(), wrld.width())
        asta = self.aStar(wrld, wrld.exitcell, sx, sy)
        if asta == -1:
            return 1
        lasta = len(asta)
        return self.renorm(math.sqrt(lasta)/math.sqrt(largestDim*4))

    # Calculate feature 7 value for state and action
    def calcFeature7(self, wrld, action, sx, sy):
        largestDim = max(wrld.height(), wrld.width())
        closestEnemy = largestDim*2
        found_enemy = False
        for e in wrld.monsters:
            asta = self.aStar(wrld, (wrld.monsters[e][0].x, wrld.monsters[e][0].y), sx, sy)
            if asta != -1:
                eDist = len(asta)
                closestEnemy = min(closestEnemy, eDist)

        return self.renorm(math.sqrt(closestEnemy)/math.sqrt(largestDim*2))

    # Calculate feature 8 value for state and action
    def calcFeature8(self, world, action, sx, sy):
        largestDim = max(world.height(), world.width())
        considerationRange = 3
        closestEnemy = considerationRange
        for e in world.monsters:
            monster = world.monsters[e][0]
            asta = self.aStar(world, (monster.x, monster.y), sx, sy)
            if asta != -1:
                eDist = len(asta)
                # Modify based on manhattan distance
                eDist += .1 * (abs(sx - monster.x) + abs(sy - monster.y))
                closestEnemy = min(closestEnemy, eDist)

        return (closestEnemy)/considerationRange

    # Calculate feature 9 value for state and action
    def calcFeature9(self, wrld, action, sx, sy):
        minCorner = 4
        minx = minCorner
        miny = minCorner
        for dx in range(minCorner):
            if (not self.valid_move(wrld, sx+dx, sy)) or (not self.valid_move(wrld, sx-dx, sy)):
                minx = min(minx, dx)
        for dy in range(minCorner):
            if (not self.valid_move(wrld, sx, sy+dy)) or (not self.valid_move(wrld, sx, sy-dy)):
                miny = min(miny, dy)
        if miny == 1 and minx == 1:
            return -1
        return math.sqrt(minx*miny)/minCorner

    # Calculate feature 10 value for state and action
    def calcFeature10(self, wrld, action, sx, sy):
        range = 6  # Adjustable range to look within 
        closestEnemy = range*2
        for e in wrld.monsters:
            xdiff = abs(wrld.monsters[e][0].x - sx)
            ydiff = abs(wrld.monsters[e][0].y - sy)
            if xdiff+ydiff < closestEnemy:
                closestEnemy = xdiff+ydiff
        
        return self.renorm(closestEnemy/(range*2))

    # Calculate feature 11 value for state and action
    def calcFeature11(self, wrld, action, sx, sy):
        feature11 = 1
        mrange = 0
        for e in wrld.monsters:
            for monster in wrld.monsters[e]:
                mrange = 0
                if monster.name == 'aggressive':
                    mrange = 2
                elif monster.name == 'selfpreserving':
                    mrange = 1

                if mrange > 0:
                    # Check if in range of aggro, based on what we think the range is
                    if abs(sx - monster.x) <= mrange and abs(sy - monster.y) <= mrange:
                        feature11 = -1.0 + .04 * (abs(sx-monster.x) + abs(sy-monster.y))

        return feature11


    ################
    # Update weights
    ################

    # Updates the weights
    def updateWeights(self, wrld, extra):
        vMoves = self.calcVMoves(wrld)
        r = self.calcReward(wrld.events, extra, is_global=True)
        maxMQ = None
        for m in range(len(vMoves)):
            if maxMQ is None:
                maxMQ = self.calcQ(wrld, vMoves[m])
            else:
                maxMQ = max(maxMQ, self.calcQ(wrld, vMoves[m]))

        print(r)

        #TODO: Should weights ever be larger than largest reward?
        if len(wrld.characters) == 0:  #abs(r) > 9000: # Find a better check for gameover
            delta = r - self.calcQ(wrld, -1)
        else:
            delta = (r + self.gamma * maxMQ) - self.calcQ(wrld, -1)
        self.printWeights()

        # Update each weight
        for i, isOn in enumerate(self.on):
            if isOn:
                self.weightArray[i] += self.lr * delta * \
                                       abs(self.featureArray[i]) * (self.weightArray[i] / abs(self.weightArray[i]))

        self.printWeights()

        self.lr = self.lr*self.decay

    ##################
    # Helper Functions
    ##################

    # Set state
    def changeState(self, on):
        self.on = on           # Weights turned on (ex. if 0 in 6th spot 6th feature turned off)
        self.weightArray = on

    # Calculates Manhattan Distance
    def calcMDist(self, x1, y1, x2, y2):
        xDist = abs(x1-x2)
        yDist = abs(y1-y2)
        return xDist + yDist

    def manhattan_distance(self, node1, node2):
        dist = abs(node1[0] - node2[0]) + abs(node1[1] - node2[1])
        return dist

    # Convert 0 to 1 num to -1 to +1 num
    def renorm(self, num):
        return num*2-1

    # Find path from current location to a goal location
    # Locations are pairs: (x, y)
    # Return a list of nodes to traverse to reach goal (including the goal)
    # or -1 indicating that the goal cannot be reached
    def aStar(self, wrld, goal, sx, sy):
        # if sx == goal[0] and sy == goal[1]:
        #    return []

        frontier = PriorityQueue()
        frontier.put((0, sx, sy))

        # Check if goal and location are the same
        if (sx, sy) == goal:
            # Return an empty list (no action / steps are needed)
            return []

        # Check if goal is in the world
        if not (0 <= goal[0] < wrld.width() and 0 <= goal[1] < wrld.height()):
            # Return indicator that goal cannot be reached
            return -1

        # Arrays are transposed to make accessing [x][y]
        cost_so_far = [[-1 for x in range(wrld.height())] for y in range(wrld.width())]
        came_from = [[(-1, -1) for x in range(wrld.height())] for y in range(wrld.width())]

        came_from[sx][sy] = 'start'
        cost_so_far[sx][sy] = 0

        while not frontier.empty():
            _, curr_x, curr_y = frontier.get()
            current = (curr_x, curr_y)

            if current == goal:
                break

            for next_node in self.neighbors(wrld, current):
                new_cost = cost_so_far[curr_x][curr_y] + 1
                curr_cost = cost_so_far[next_node[0]][next_node[1]]
                if curr_cost == -1 or new_cost < curr_cost:
                    cost_so_far[next_node[0]][next_node[1]] = new_cost
                    priority = new_cost + self.manhattan_distance(goal, next_node)
                    frontier.put((priority, next_node[0], next_node[1]))
                    came_from[next_node[0]][next_node[1]] = current

        prev_node = came_from[goal[0]][goal[1]]
        # Check if goal is not reachable
        if prev_node == (-1, -1):
            # Return indicator that goal is not reachable
            return -1

        # Construct path from came_from
        path = [(goal[0], goal[1])]
        while prev_node != (sx, sy):
            path.append(prev_node)
            prev_node = came_from[prev_node[0]][prev_node[1]]

        return path

    # Return all non-wall Neighbors
    def neighbors(self, wrld, node):
        neighbors = []

        for dx in [-1, 0, 1]:
            # Avoid out-of-bound indexing
            if (node[0] + dx >= 0) and (node[0] + dx < wrld.width()):
                # Loop through delta y
                for dy in [-1, 0, 1]:
                    # Make sure the monster is moving
                    if (dx != 0) or (dy != 0):
                        # Avoid out-of-bound indexing
                        if (node[1] + dy >= 0) and (node[1] + dy < wrld.height()):
                            # No need to check impossible moves
                            if self.valid_move(wrld, node[0] + dx, node[1] + dy):
                                neighbors.append((node[0] + dx, node[1] + dy))

        return neighbors

    # Return # of bordering walls
    def surroundingWallCount(self, wrld, node):
        neighboringWalls = 0

        for dx in [-1, 0, 1]:
            # Avoid out-of-bound indexing
            if (node[0] + dx >= 0) and (node[0] + dx < wrld.width()):
                # Loop through delta y
                for dy in [-1, 0, 1]:
                    # Make sure the monster is moving
                    if (dx != 0) or (dy != 0):
                        # Avoid out-of-bound indexing
                        if (node[1] + dy >= 0) and (node[1] + dy < wrld.height()):
                            # No need to check impossible moves
                            if wrld.wall_at(node[0] + dx, node[1] + dy):
                                neighboringWalls += 1

        return neighboringWalls

    # Determine if self can move to world position x,y
    def valid_move(self, wrld, x, y):
        return x >= 0 and x < wrld.width() and y >= 0 and y < wrld.height() and not wrld.wall_at(x,y) and not wrld.explosion_at(x,y)

    # Returns true if there's a bomb at given position
    def is_bomb_at(self, wrld, x, y):
        for b in wrld.bombs:
            if wrld.bombs[b].x == x and wrld.bombs[b].y == y:
                return True

    # Execute move dictated by action
    def makeMove(self, action, char=None):
        if char is None:
            char = self
        # Action is in the form (dx, dy, should_place_bomb)
        char.move(action[0], action[1])
        if action[2]:
            char.place_bomb()

    # Calculate valid moves
    # Moves take the form (dx, dy, should_place_bomb)
    def calcVMoves(self, wrld):
        validMoves = []

        # Loop through delta x
        for dx in [-1, 0, 1]:
            # Loop through delta y
            for dy in [-1, 0, 1]:
                if self.valid_move(wrld, self.x + dx, self.y + dy):
                    validMoves.append((dx, dy, False))
                    # If a bomb can be placed
                    if wrld.bomb_time == 10:
                        # Then can also bomb and move
                        validMoves.append((dx, dy, True))

        return validMoves

    # Prints out the weights
    def printWeights(self):
        print("Weights: " + str(self.weightArray))

    # Prints out the features
    def printFeatures(self):
        print("Features: " + str(self.featureArray))

    # Calculates the reward given events
    def calcReward(self, events, extra, is_global=False):
        r = -1 + extra  # cost of living + extra reward
        for e in range(len(events)):
            if events[e].tpe == 0:
                r += 100  # BOMB_HIT_WALL
            elif events[e].tpe == 1:
                r += 1000  # BOMB_HIT_MONSTER
            elif events[e].tpe == 2:
                r -= 11000  # BOMB_HIT_CHARACTER
                if is_global:
                    self.gameOver(False)  # Loss
            elif events[e].tpe == 3:
                r -= 10000  # CHARACTER_KILLED_BY_MONSTER
                if is_global:
                    self.gameOver(False)  # Loss
            elif events[e].tpe == 4:
                r += 10000  # CHARACTER_FOUND_EXIT
                if is_global:
                    self.gameOver(True)  # Win
            print(events[e])
        return r

    # Saves current weight values to state determined by number
    def saveOldState(self, num):
        if num == 1:
            self.oldstate1 = self.weightArray
        elif num == 2:
            self.oldState2 = self.weightArray

    # Handle game end
    def gameOver(self, win):
        if win:
            self.wins += 1
        else:
            self.losses += 1

        print("Win Percentage across " + str(self.wins+self.losses) + " games: " + str((self.wins/(self.wins+self.losses))*100) + "%")
        # Save state for next run
        self.saveOldState(self.state)


