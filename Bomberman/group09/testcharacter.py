# This is necessary to find the main code
import sys
sys.path.insert(0, '../bomberman')
# Import necessary stuff
from entity import CharacterEntity
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
   Add feature spot to ALL on arrays
'''

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
        print(hMove)

        # Learning
        qMove = -1
        if(self.lr == 0.0 or random.randint(0, 5) != 0):  # Add some randomness
            maxQ = None
            for m in range(len(validMoves)):
                moveQVal = self.calcQ(wrld, validMoves[m])
                if maxQ == None or moveQVal > maxQ:
                    qMove = validMoves[m]
                    maxQ = moveQVal
        else:
            print("Random")



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

        is_global = False
        if action == -1:
            is_global = True
        else:   # Only do if action taken/ time passed
            if action == 0 or action == 1 or action == 2 or action == 6:
                sx += 0
            elif action == 3 or action == 4 or action == 5:
                sx += 1
            elif action == 7 or action == 8 or action == 9:
                sx -= 1

            if action == 0 or action == 1 or action == 4 or action == 8:
                sy += 0
            elif action == 5 or action == 6 or action == 7:
                sy -= 1
            elif action == 2 or action == 3 or action == 9:
                sy += 1

        # Enemy dist
        feature9 = 0.0
        if (self.on[8] != 0):
            if is_global:
                self.feature9 = self.calcFeature9(wrld, action, sx, sy)
            else:
                feature9 = self.calcFeature9(wrld, action, sx, sy)

        # Enemy dist
        feature8 = 0.0
        if (self.on[7] != 0):
            if is_global:
                self.feature8 = self.calcFeature8(wrld, action, sx, sy, False)
            else:
                feature8 = self.calcFeature8(wrld, action, sx, sy, True)

        # Enemy dist
        feature7 = 0.0
        if (self.on[6] != 0):
            if is_global:
                self.feature7 = self.calcFeature7(wrld, action, sx, sy, False, self.alt7)
            else:
                feature7 = self.calcFeature7(wrld, action, sx, sy, True, self.alt7)

        # A*
        feature6 = 0.0
        if(self.on[5] != 0):
            if is_global:
                self.feature6 = self.calcFeature6(wrld, action, sx, sy)
            else:
                feature6 = self.calcFeature6(wrld, action, sx, sy)

        # Bombs on the field
        feature5 = 0.0
        if (self.on[4] != 0):
            if is_global:
                self.feature5 = self.calcFeature5(wrld, action, sx, sy)
            else:
                feature5 = self.calcFeature5(wrld, action, sx, sy)

        # Dist from side walls
        feature4 = 0.0
        if (self.on[3] != 0):
            if is_global:
                self.feature4 = self.calcFeature4(wrld, action, sx, sy)
            else:
                feature4 = self.calcFeature4(wrld, action, sx, sy)

        # neighboring walls
        feature3 = 0.0
        if (self.on[2] != 0):
            if is_global:
                self.feature3 = self.calcFeature3(wrld, action, sx, sy)
            else:
                feature3 = self.calcFeature3(wrld, action, sx, sy)

        # bomb dist on lines calc
        feature2 = 0.0
        if (self.on[1] != 0):
            if is_global:
                self.feature2 = self.calcFeature2(wrld, action, sx, sy)
            else:
                feature2 = self.calcFeature2(wrld, action, sx, sy)

        # Manhattan dist calc
        feature1 = 0.0
        if (self.on[0] != 0):
            if is_global:
                self.feature1 = self.calcFeature1(wrld, action, sx, sy)
            else:
                feature1 = self.calcFeature1(wrld, action, sx, sy)

        if (is_global):
            return self.weight1 * self.feature1 + self.weight2 * self.feature2 + self.weight3 * self.feature3 + self.weight4 * self.feature4 + self.weight5 * self.feature5 + self.weight6 * self.feature6 + self.weight7 * self.feature7 + self.weight8 * self.feature8 + self.weight9 * self.feature9
        else:
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
        if action == 1:
            value = 0
        value = self.renorm(value)
        return -value

    # Calculate feature 6 value for state and action
    def calcFeature6(self, wrld, action, sx, sy):
        largestDim = max(wrld.height(), wrld.width())
        asta = self.aStar(wrld, wrld.exitcell, sx, sy)
        lasta = len(asta)
        return -self.renorm(math.sqrt(lasta)/math.sqrt(largestDim*4))

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
            if not self.valid_move(wrld, sx+dx, sy) or not self.valid_move(wrld, sx+dx, sy):
                minx = min(minx, dx)
        for dy in range(minCorner):
            if not self.valid_move(wrld, sx, sy+dy) or not self.valid_move(wrld, sx, sy+dy):
                miny = min(miny, dy)
        return math.sqrt(minx*miny)/minCorner


    ################
    # Update weights
    ################

    # Updates the weights
    def updateWeights(self, wrld, extra):
        vMoves = self.calcVMoves(wrld)
        r = -1 + extra  # cost of living
        for e in range(len(wrld.events)):
            if wrld.events[e].tpe == 0:
                r += 100  # BOMB_HIT_WALL
            if wrld.events[e].tpe == 1:
                r += 1000  # BOMB_HIT_MONSTER
            if wrld.events[e].tpe == 2:
                r -= 10000  # BOMB_HIT_CHARACTER
                self.losses += 1
            if wrld.events[e].tpe == 3:
                r -= 10000  # CHARACTER_KILLED_BY_MONSTER
                self.losses += 1
            if wrld.events[e].tpe == 4:
                r += 10000  # CHARACTER_FOUND_EXIT
                self.wins += 1
            print(wrld.events[e])
        maxMQ = 0;
        for m in range(len(vMoves)):
            if m == 0:
                maxMQ = self.calcQ(wrld, vMoves[m])
            else:
                maxMQ = max(maxMQ, self.calcQ(wrld, vMoves[m]))

        print(r)

        #TODO: Right now positive weights adjust correctly but negative weights always just get more megative (Possibly fixed?)
        delta = (r + self.gamma * maxMQ) - self.calcQ(wrld, -1)
        self.printWeights()

        if (self.on[0] != 0):
            self.weight1 = self.weight1 + self.lr * delta * self.feature1 * (self.weight1/abs(self.weight1))
        if (self.on[1] != 0):
            self.weight2 = self.weight2 + self.lr * delta * self.feature2 * (self.weight2/abs(self.weight2))
        if (self.on[2] != 0):
            self.weight3 = self.weight3 + self.lr * delta * self.feature3 * (self.weight3/abs(self.weight3))
        if (self.on[3] != 0):
            self.weight4 = self.weight4 + self.lr * delta * self.feature4 * (self.weight4/abs(self.weight4))
        if (self.on[4] != 0):
            self.weight5 = self.weight5 + self.lr * delta * self.feature5 * (self.weight5/abs(self.weight5))
        if (self.on[5] != 0):
            self.weight6 = self.weight6 + self.lr * delta * self.feature6 * (self.weight6/abs(self.weight6))
        if (self.on[6] != 0):
            self.weight7 = self.weight7 + self.lr * delta * self.feature7 * (self.weight7/abs(self.weight7))
        if (self.on[7] != 0):
            self.weight8 = self.weight8 + self.lr * delta * self.feature8 * (self.weight8/abs(self.weight8))
        if (self.on[8] != 0):
            self.weight9 = self.weight9 + self.lr * delta * self.feature9 * (self.weight9/abs(self.weight9))

        self.printWeights()

        self.lr = self.lr*self.decay


    ##################
    # Helper Functions
    ##################

    # Set state
    def changeState(self, on):
        self.on = on           # Weights turned on (ex. if 0 in 6th spot 6th feature turned off)
        self.weight1 = on[0]   # Weight 1 (exit dist)
        self.weight2 = on[1]   # Weight 2 (bomb dist)
        self.weight3 = on[2]   # Weight 3 (nearby walls)
        self.weight4 = on[3]   # Weight 4 (side wall dist)
        self.weight5 = on[4]   # Weight 5 (num bombs)
        self.weight6 = on[5]   # Weight 6 (a*)
        self.weight7 = on[6]   # Weight 7 (enemy dist)

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
        return x >= 0 and x < wrld.width() and y >= 0 and y < wrld.height() and not wrld.wall_at(x,y)

    # Returns true if there's a bomb at given position
    def is_bomb_at(self, wrld, x, y):
        for b in wrld.bombs:
            if wrld.bombs[b].x == x and wrld.bombs[b].y == y:
                return True

    # Execute move dictated by action
    def makeMove(self, action):
        if (action == 0):
            pass
        elif (action == 1):
            self.place_bomb()
        elif (action == 2):
            self.move(0, 1)
        elif (action == 3):
            self.move(1, 1)
        elif (action == 4):
            self.move(1, 0)
        elif (action == 5):
            self.move(1, -1)
        elif (action == 6):
            self.move(0, -1)
        elif (action == 7):
            self.move(-1, -1)
        elif (action == 8):
            self.move(-1, 0)
        elif (action == 9):
            self.move(-1, 1)
        else:
            pass

    # Calculate valid moves
    def calcVMoves(self, wrld):
        validMoves = []
        validMoves.append(0)  # Pass is valid
        if (wrld.bomb_time == 10):
            validMoves.append(1)  # Place bomb is valid
        if (self.valid_move(wrld, self.x, self.y + 1)):
            validMoves.append(2)  # Move down is valid
        if (self.valid_move(wrld, self.x + 1, self.y + 1)):
            validMoves.append(3)  # Move down & right is valid
        if (self.valid_move(wrld, self.x + 1, self.y)):
            validMoves.append(4)  # Move right is valid
        if (self.valid_move(wrld, self.x + 1, self.y - 1)):
            validMoves.append(5)  # Move up & right is valid
        if (self.valid_move(wrld, self.x, self.y - 1)):
            validMoves.append(6)  # Move up is valid
        if (self.valid_move(wrld, self.x - 1, self.y - 1)):
            validMoves.append(7)  # Move up & left is valid
        if (self.valid_move(wrld, self.x - 1, self.y)):
            validMoves.append(8)  # Move left is valid
        if (self.valid_move(wrld, self.x - 1, self.y + 1)):
            validMoves.append(9)  # Move down & left is valid

        return validMoves

    # Prints out the weights
    def printWeights(self):
        print("New Weights: [" + str(self.weight1) + ", " + str(self.weight2) + ", " + str(self.weight3) + ", " +
            str(self.weight4) + ", " + str(self.weight5) + ", " + str(self.weight6) + ", " + str(self.weight7) + ", " +
            str(self.weight8) + ", " + str(self.weight9) + "]")



