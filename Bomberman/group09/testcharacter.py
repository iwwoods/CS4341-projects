# This is necessary to find the main code
import sys
sys.path.insert(0, '../bomberman')
# Import necessary stuff
from entity import CharacterEntity
from sensed_world import SensedWorld
from colorama import Fore, Back
import random
import math
from queue import PriorityQueue


'''
 To add feature:
   Add weight and feature variables to init,
   Add calcFeatureN function
   Add feature calculation and add feature * weight to the result of calcQ
   Add feature to update weights function
   Add feature to the print weights helper function
   Add feature to changeState helper
   Add feature spot to ALL on arrays
'''

#TODO: When enemy lockes on its pretty much impossible to not die, Find a way around this, maybe look at enemy's code and find what causes lock on
#TODO: Add feature 10, manhattan dist to enemy in range (7?)
#TODO: Ensure code all works when door isnt visible
#TODO: Add state change for when door is visible or not
#TODO: Add feature 11, number of walls inside range n (n = bomb range)

class TestCharacter(CharacterEntity):
    def __init__(self, name, avatar, x, y, on, decay, lr):
        CharacterEntity.__init__(self, name, avatar, x, y)
        self.on = on       # Weights turned on (if 0 in 6th spot 6th feature turned off
        self.weight1 = on[0]   # Weight 1 (exit dist)
        self.weight2 = on[1]   # Weight 2 (bomb dist)
        self.weight3 = on[2]   # Weight 3 (nearby walls)
        self.weight4 = on[3]   # Weight 4 (side wall dist)
        self.weight5 = on[4]   # Weight 5 (num bombs)
        self.weight6 = on[5]   # Weight 6 (a*)
        self.weight7 = on[6]   # Weight 7 (enemy dist)
        self.weight8 = on[7]   # Weight 8 (enemy in range 5 dist)
        self.weight9 = on[8]   # Weight 9 (corner detection)
        self.feature1 = 0.0     # Manhattan distance to door
        self.feature2 = 0.0     # Manhattan distance to bomb in col/row
        self.feature3 = 0.0     # number of neighboring walls
        self.feature4 = 0.0     # distance from closest side wall
        self.feature5 = 0.0     # number bombs on the field
        self.feature6 = 0.0     # A*
        self.feature7 = 0.0     # Closest enemy
        self.feature8 = 0.0     # Closest enemy in range of 5
        self.feature9 = 0.0     # Corner detection
        self.gamma = 0.9        # Reward Decay
        self.lr = lr            # Learning Rate
        self.decay = decay      # Decay
        self.wins = 0           # Number of wins so far
        self.losses = 0         # Number of losses so far
        self.alt7 = False       # True if enemies are moving only in straight lines
        self.debug = True

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
        # TODO: Determine why he always places a bomb at the beginning even when bomb features are turned off
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
        elif move < len(validMoves) :
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

        # Corner detection
        feature9 = 0.0
        if (self.on[8] != 0):
            if is_global:
                self.feature9 = self.calcFeature9(world, action, sx, sy)
            else:
                feature9 = self.calcFeature9(world, action, sx, sy)

        # Closest enemy in range of 3
        feature8 = 0.0
        if (self.on[7] != 0):
            if is_global:
                self.feature8 = self.calcFeature8(world, action, sx, sy, False)
            else:
                feature8 = self.calcFeature8(world, action, sx, sy, True)

        # Enemy dist
        feature7 = 0.0
        if (self.on[6] != 0):
            if is_global:
                self.feature7 = self.calcFeature7(world, action, sx, sy, False, self.alt7)
            else:
                feature7 = self.calcFeature7(world, action, sx, sy, True, self.alt7)

        # A*
        feature6 = 0.0
        if(self.on[5] != 0):
            if is_global:
                self.feature6 = self.calcFeature6(world, action, sx, sy)
            else:
                feature6 = self.calcFeature6(world, action, sx, sy)

        # Bombs on the field
        feature5 = 0.0
        if (self.on[4] != 0):
            if is_global:
                self.feature5 = self.calcFeature5(world, action, sx, sy)
            else:
                feature5 = self.calcFeature5(world, action, sx, sy)

        # Dist from side walls
        feature4 = 0.0
        if (self.on[3] != 0):
            if is_global:
                self.feature4 = self.calcFeature4(world, action, sx, sy)
            else:
                feature4 = self.calcFeature4(world, action, sx, sy)

        # neighboring walls
        feature3 = 0.0
        if (self.on[2] != 0):
            if is_global:
                self.feature3 = self.calcFeature3(world, action, sx, sy)
            else:
                feature3 = self.calcFeature3(world, action, sx, sy)

        # bomb dist on lines calc
        feature2 = 0.0
        if (self.on[1] != 0):
            if is_global:
                self.feature2 = self.calcFeature2(world, action, sx, sy)
            else:
                feature2 = self.calcFeature2(world, action, sx, sy)

        # Manhattan dist calc
        feature1 = 0.0
        if (self.on[0] != 0):
            if is_global:
                self.feature1 = self.calcFeature1(world, action, sx, sy)
            else:
                feature1 = self.calcFeature1(world, action, sx, sy)

        # Change state under certain conditions
        if action == -1:
            enemyDist = None
            goalDist = 0

            # Fill goalDist
            if (self.on[5] != 0):
                goalDist = self.feature6
            else:
                goalDist = self.calcFeature6(world, action, sx, sy)

            # Fill enemyDist (enemy to door)
            for e in world.monsters:
                if enemyDist is None:
                    enemyDist = len(self.aStar(world, world.exitcell, world.monsters[e][0].x, world.monsters[e][0].y))
                else:
                    enemyDist = min(enemyDist, len(self.aStar(world, world.exitcell, world.monsters[e][0].x, world.monsters[e][0].y)))

            if enemyDist is not None and enemyDist != 0:
                largestDim = max(world.height(), world.width())
                enemyDist = enemyDist-1  # Monster moves first
                enemyDist = self.renorm(math.sqrt(enemyDist) / math.sqrt(largestDim * 4))

            if enemyDist is None or enemyDist == 0 or goalDist < enemyDist:
                self.changeState([0.0, 0.0, 0.0, 0.0, 0.0, -5.0, 0.0, 0.0, 0.0])  # Go straight to goal


        if (is_global):
            # if self.debug:
                # self.printFeatures()
            return self.weight1 * self.feature1 + self.weight2 * self.feature2 + self.weight3 * self.feature3 + self.weight4 * self.feature4 + self.weight5 * self.feature5 + self.weight6 * self.feature6 + self.weight7 * self.feature7 + self.weight8 * self.feature8 + self.weight9 * self.feature9
        else:
            if self.debug:
                print("Features: [" + str(feature1) + ", " + str(feature2) + ", " + str(feature3) + ", " +
                  str(feature4) + ", " + str(feature5) + ", " + str(feature6) + ", " + str(feature7) + ", " +
                  str(feature8) + ", " + str(feature9) + "]")
            return self.weight1 * feature1 + self.weight2 * feature2 + self.weight3 * feature3 + self.weight4 * feature4 + self.weight5 * feature5 + self.weight6 * feature6 + self.weight7 * feature7 + self.weight8 * feature8 + self.weight9 * feature9


    #####################
    # Feature Calculation
    #####################

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
        ticksToIgnore = 4  # ignores bomb positioning for first four seconds to allow free movement
        feature2 = wrld.bomb_time-ticksToIgnore
        for k in wrld.bombs:
            if wrld.bombs[k].x == sx:
                if abs(wrld.bombs[k].y - sy) <= range:
                    feature2 = wrld.bombs[k].timer
            if wrld.bombs[k].y == sy:
                if abs(wrld.bombs[k].x - sx) <= range:
                    feature2 = wrld.bombs[k].timer
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
        value = 1
        for b in wrld.bombs:
            value = 0
        value = self.renorm(value)
        return -value

    # Calculate feature 6 value for state and action
    def calcFeature6(self, wrld, action, sx, sy):
        largestDim = max(wrld.height(), wrld.width())
        asta = self.aStar(wrld, wrld.exitcell, sx, sy)
        lasta = len(asta)
        return self.renorm(math.sqrt(lasta)/math.sqrt(largestDim*4))

    # Calculate feature 7 value for state and action
    def calcFeature7(self, wrld, action, sx, sy, enemy_moves, dir=False):
        largestDim = max(wrld.height(), wrld.width())
        closestEnemy = largestDim*2
        for e in wrld.monsters:
            if dir == False:
                closestEnemy = min(closestEnemy, len(self.aStar(wrld, (wrld.monsters[e][0].x, wrld.monsters[e][0].y), sx, sy)))
            else:
                nx = wrld.monsters[e][0].x + wrld.monsters[e][0].dx
                ny = wrld.monsters[e][0].y + wrld.monsters[e][0].dy
                if nx >= 0 and nx < wrld.width() and ny >= 0 and ny < wrld.height() and not wrld.wall_at(nx, ny):
                    asta = self.aStar(wrld, (nx, ny), sx, sy)
                    if asta != -1:
                        closestEnemy = min(closestEnemy, len(asta))
                else:
                    asta = self.aStar(wrld, (wrld.monsters[e][0].x, wrld.monsters[e][0].y), sx, sy)
                    if asta != -1:
                        closestEnemy = min(closestEnemy, len(asta))

        # Account for worst case if enemy moves
        if enemy_moves and closestEnemy > 0 and dir == False:
            closestEnemy -= 1

        return self.renorm(math.sqrt(closestEnemy)/math.sqrt(largestDim*2))

    # Calculate feature 8 value for state and action
    def calcFeature8(self, wrld, action, sx, sy, enemy_moves):
        largestDim = max(wrld.height(), wrld.width())
        considerationRange = 3
        closestEnemy = considerationRange
        if enemy_moves:
            closestEnemy += 1
        for e in wrld.monsters:
            asta = self.aStar(wrld, (wrld.monsters[e][0].x, wrld.monsters[e][0].y), sx, sy)
            if asta != -1:
                closestEnemy = min(closestEnemy, len(asta))

        # Account for worst case if enemy moves
        if enemy_moves and closestEnemy > 0:
            closestEnemy -= 1

        return (closestEnemy)/considerationRange

    # Calculate feature 9 value for state and action
    def calcFeature9(self, wrld, action, sx, sy):
        minCorner = 4
        minx = minCorner
        miny = minCorner
        for dx in range(minCorner):
            if (not self.valid_move(wrld, sx+dx, sy)) or (not self.valid_move(wrld, sx+dx, sy)):
                minx = min(minx, dx)
        for dy in range(minCorner):
            if (not self.valid_move(wrld, sx, sy+dy)) or (not self.valid_move(wrld, sx, sy+dy)):
                miny = min(miny, dy)
        return math.sqrt(minx*miny)/minCorner


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

        if (self.on[0] != 0):
            self.weight1 = self.weight1 + self.lr * delta * abs(self.feature1) * (self.weight1/abs(self.weight1))
        if (self.on[1] != 0):
            self.weight2 = self.weight2 + self.lr * delta * abs(self.feature2) * (self.weight2/abs(self.weight2))
        if (self.on[2] != 0):
            self.weight3 = self.weight3 + self.lr * delta * abs(self.feature3) * (self.weight3/abs(self.weight3))
        if (self.on[3] != 0):
            self.weight4 = self.weight4 + self.lr * delta * abs(self.feature4) * (self.weight4/abs(self.weight4))
        if (self.on[4] != 0):
            self.weight5 = self.weight5 + self.lr * delta * abs(self.feature5) * (self.weight5/abs(self.weight5))
        if (self.on[5] != 0):
            self.weight6 = self.weight6 + self.lr * delta * abs(self.feature6) * (self.weight6/abs(self.weight6))
        if (self.on[6] != 0):
            self.weight7 = self.weight7 + self.lr * delta * abs(self.feature7) * (self.weight7/abs(self.weight7))
        if (self.on[7] != 0):
            self.weight8 = self.weight8 + self.lr * delta * abs(self.feature8) * (self.weight8/abs(self.weight8))
        if (self.on[8] != 0):
            self.weight9 = self.weight9 + self.lr * delta * abs(self.feature9) * (self.weight9/abs(self.weight9))

        self.printWeights()

        self.lr = self.lr*self.decay


    ##################
    # Helper Functions
    ##################

    # Set state
    def changeState(self, on):
        self.on = on           # Weights turned on (ex. if 0 in 6th spot 6th feature turned off)
        self.weight1 = on[0]   # Weight 1 (exit dist)
        self.weight2 = on[1]   # Weight 2 (bomb in range?)
        self.weight3 = on[2]   # Weight 3 (nearby walls)
        self.weight4 = on[3]   # Weight 4 (side wall dist)
        self.weight5 = on[4]   # Weight 5 (num bombs)
        self.weight6 = on[5]   # Weight 6 (a*)
        self.weight7 = on[6]   # Weight 7 (enemy dist)
        self.weight8 = on[7]   # Weight 8 (enemy in range 5 dist)
        self.weight9 = on[8]   # Weight 9 (corner detection)

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
                            if not wrld.wall_at(node[0] + dx, node[1] + dy):
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
            if (action == 1):
                self.move(0, 1)
            elif (action == 2):
                self.move(1, 1)
            elif (action == 3):
                self.move(1, 0)
            elif (action == 4):
                self.move(1, -1)
            elif (action == 5):
                self.move(0, -1)
            elif (action == 6):
                self.move(-1, -1)
            elif (action == 7):
                self.move(-1, 0)
            elif (action == 8):
                self.move(-1, 1)
            elif (action == 10):
                self.place_bomb()
                self.move(0,0)
            elif (action == 11):
                self.place_bomb()
                self.move(0, 1)
            elif (action == 12):
                self.place_bomb()
                self.move(1, 1)
            elif (action == 13):
                self.place_bomb()
                self.move(1, 0)
            elif (action == 14):
                self.place_bomb()
                self.move(1, -1)
            elif (action == 15):
                self.place_bomb()
                self.move(0, -1)
            elif (action == 16):
                self.place_bomb()
                self.move(-1, -1)
            elif (action == 17):
                self.place_bomb()
                self.move(-1, 0)
            elif (action == 18):
                self.place_bomb()
                self.move(-1, 1)
            else:
                self.move(0,0)
        else:
            if (action == 1):
                char.move(0, 1)
            elif (action == 2):
                char.move(1, 1)
            elif (action == 3):
                char.move(1, 0)
            elif (action == 4):
                char.move(1, -1)
            elif (action == 5):
                char.move(0, -1)
            elif (action == 6):
                char.move(-1, -1)
            elif (action == 7):
                char.move(-1, 0)
            elif (action == 8):
                char.move(-1, 1)
            elif (action == 10):
                char.place_bomb()
                char.move(0,0)
            elif (action == 11):
                char.place_bomb()
                char.move(0, 1)
            elif (action == 12):
                char.place_bomb()
                char.move(1, 1)
            elif (action == 13):
                char.place_bomb()
                char.move(1, 0)
            elif (action == 14):
                char.place_bomb()
                char.move(1, -1)
            elif (action == 15):
                char.place_bomb()
                char.move(0, -1)
            elif (action == 16):
                char.place_bomb()
                char.move(-1, -1)
            elif (action == 17):
                char.place_bomb()
                char.move(-1, 0)
            elif (action == 18):
                char.place_bomb()
                char.move(-1, 1)
            else:
                char.move(0,0)

    # Calculate valid moves
    def calcVMoves(self, wrld):
        validMoves = []
        validMoves.append(0)  # No move is valid
        if (self.valid_move(wrld, self.x, self.y + 1)):
            validMoves.append(1)  # Move down is valid
        if (self.valid_move(wrld, self.x + 1, self.y + 1)):
            validMoves.append(2)  # Move down & right is valid
        if (self.valid_move(wrld, self.x + 1, self.y)):
            validMoves.append(3)  # Move right is valid
        if (self.valid_move(wrld, self.x + 1, self.y - 1)):
            validMoves.append(4)  # Move up & right is valid
        if (self.valid_move(wrld, self.x, self.y - 1)):
            validMoves.append(5)  # Move up is valid
        if (self.valid_move(wrld, self.x - 1, self.y - 1)):
            validMoves.append(6)  # Move up & left is valid
        if (self.valid_move(wrld, self.x - 1, self.y)):
            validMoves.append(7)  # Move left is valid
        if (self.valid_move(wrld, self.x - 1, self.y + 1)):
            validMoves.append(8)  # Move down & left is valid
        if (wrld.bomb_time == 10):
            validMoves.append(10)  # Place bomb and no move is valid
            if (self.valid_move(wrld, self.x, self.y + 1)):
                validMoves.append(11)  # Move down is valid
            if (self.valid_move(wrld, self.x + 1, self.y + 1)):
                validMoves.append(12)  # Move down & right is valid
            if (self.valid_move(wrld, self.x + 1, self.y)):
                validMoves.append(13)  # Move right is valid
            if (self.valid_move(wrld, self.x + 1, self.y - 1)):
                validMoves.append(14)  # Move up & right is valid
            if (self.valid_move(wrld, self.x, self.y - 1)):
                validMoves.append(15)  # Move up is valid
            if (self.valid_move(wrld, self.x - 1, self.y - 1)):
                validMoves.append(16)  # Move up & left is valid
            if (self.valid_move(wrld, self.x - 1, self.y)):
                validMoves.append(17)  # Move left is valid
            if (self.valid_move(wrld, self.x - 1, self.y + 1)):
                validMoves.append(18)  # Move down & left is valid   
        return validMoves

    # Prints out the weights
    def printWeights(self):
        print("Weights: [" + str(self.weight1) + ", " + str(self.weight2) + ", " + str(self.weight3) + ", " +
            str(self.weight4) + ", " + str(self.weight5) + ", " + str(self.weight6) + ", " + str(self.weight7) + ", " +
            str(self.weight8) + ", " + str(self.weight9) + "]")
        
    # Prints out the features
    def printFeatures(self):
        print("Features: [" + str(self.feature1) + ", " + str(self.feature2) + ", " + str(self.feature3) + ", " +
            str(self.feature4) + ", " + str(self.feature5) + ", " + str(self.feature6) + ", " + str(self.feature7) + ", " +
            str(self.feature8) + ", " + str(self.feature9) + "]")

    # Calculates the reward given events
    def calcReward(self, events, extra, is_global=False):
        r = -1 + extra  # cost of living + extra reward
        for e in range(len(events)):
            if events[e].tpe == 0:
                r += 100  # BOMB_HIT_WALL
            elif events[e].tpe == 1:
                r += 1000  # BOMB_HIT_MONSTER
            elif events[e].tpe == 2:
                r -= 10000  # BOMB_HIT_CHARACTER
                if is_global:
                    self.losses += 1
            elif events[e].tpe == 3:
                r -= 10000  # CHARACTER_KILLED_BY_MONSTER
                if is_global:
                    self.losses += 1
            elif events[e].tpe == 4:
                r += 10000  # CHARACTER_FOUND_EXIT
                if is_global:
                    self.wins += 1
            print(events[e])
        return r

