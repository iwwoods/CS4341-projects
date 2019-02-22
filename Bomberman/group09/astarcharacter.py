# This is necessary to find the main code
import sys
from queue import PriorityQueue
sys.path.insert(0, '../bomberman')
# Import necessary stuff
from entity import CharacterEntity


class AStarCharacter(CharacterEntity):
    path = []

    def do(self, wrld):
        # Your code here
        # Find the goal
        goal = self.find_goal(wrld)

        if self.path == -1 or len(self.path) < 1:
            self.path = self.aStar(wrld, goal)

        # Calculate movement dx, dy
        if self.path != -1:
            my_loc = wrld.me(self)
            next_node = self.path.pop()
            dx = next_node[0] - my_loc.x
            dy = next_node[1] - my_loc.y
            self.move(dx, dy)

        pass

    # Find path from current location to a goal location
    # Locations are pairs: (x, y)
    # Return a list of nodes to traverse to reach goal (including the goal)
    # or -1 indicating that the goal cannot be reached
    def aStar(self, wrld, goal):
        frontier = PriorityQueue()
        my_loc = wrld.me(self)
        frontier.put((0, my_loc.x, my_loc.y))

        # Check if goal and location are the same
        if (my_loc.x, my_loc.y) == goal:
            # Return an empty list (no action / steps are needed)
            return []

        # Check if goal is in the world
        if not (0 <= goal[0] < wrld.width() and 0 <= goal[1] < wrld.height()):
            # Return indicator that goal cannot be reached
            return -1

        # Arrays are transposed to make accessing [x][y]
        cost_so_far = [[-1 for x in range(wrld.height())] for y in range(wrld.width())]
        came_from = [[(-1, -1) for x in range(wrld.height())] for y in range(wrld.width())]

        came_from[my_loc.x][my_loc.y] = 'start'
        cost_so_far[my_loc.x][my_loc.y] = 0

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
        while prev_node != (my_loc.x, my_loc.y):
            path.append(prev_node)
            prev_node = came_from[prev_node[0]][prev_node[1]]

        return path

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

    def manhattan_distance(self, node1, node2):
        dist = abs(node1[0] - node2[0]) + \
               abs(node1[1] - node2[1])
        return dist

    def find_goal(self, wrld):
        return wrld.width()-1, wrld.height()-1
