from __future__ import print_function
from wekaI import Weka

# bustersAgents.py
# ----------------
# Licensing Information:  You are free to use or extend these projects for
# educational purposes provided that (1) you do not distribute or publish
# solutions, (2) you retain this notice, and (3) you provide clear
# attribution to UC Berkeley.
# 
# Attribution Information: The Pacman AI projects were developed at UC Berkeley.
# The core projects and autograders were primarily created by John DeNero
# (denero@cs.berkeley.edu) and Dan Klein (klein@cs.berkeley.edu).
# Student side autograding was added by Brad Miller, Nick Hay, and
# Pieter Abbeel (pabbeel@cs.berkeley.edu).


from builtins import range
from builtins import object
import util
from game import Agent
from game import Directions
from keyboardAgents import KeyboardAgent
import inference
import busters

class NullGraphics(object):
    "Placeholder for graphics"
    def initialize(self, state, isBlue = False):
        pass
    def update(self, state):
        pass
    def pause(self):
        pass
    def draw(self, state):
        pass
    def updateDistributions(self, dist):
        pass
    def finish(self):
        pass

class KeyboardInference(inference.InferenceModule):
    """
    Basic inference module for use with the keyboard.
    """
    def initializeUniformly(self, gameState):
        "Begin with a uniform distribution over ghost positions."
        self.beliefs = util.Counter()
        for p in self.legalPositions: self.beliefs[p] = 1.0
        self.beliefs.normalize()

    def observe(self, observation, gameState):
        noisyDistance = observation
        emissionModel = busters.getObservationDistribution(noisyDistance)
        pacmanPosition = gameState.getPacmanPosition()
        allPossible = util.Counter()
        for p in self.legalPositions:
            trueDistance = util.manhattanDistance(p, pacmanPosition)
            if emissionModel[trueDistance] > 0:
                allPossible[p] = 1.0
        allPossible.normalize()
        self.beliefs = allPossible

    def elapseTime(self, gameState):
        pass

    def getBeliefDistribution(self):
        return self.beliefs


class BustersAgent(object):
    "An agent that tracks and displays its beliefs about ghost positions."

    def __init__( self, index = 0, inference = "ExactInference", ghostAgents = None, observeEnable = True, elapseTimeEnable = True):
        self.weka = Weka()
        self.weka.start_jvm()
        inferenceType = util.lookup(inference, globals())
        self.inferenceModules = [inferenceType(a) for a in ghostAgents]
        self.observeEnable = observeEnable
        self.elapseTimeEnable = elapseTimeEnable

    def registerInitialState(self, gameState):
        "Initializes beliefs and inference modules"
        import __main__
        self.display = __main__._display
        for inference in self.inferenceModules:
            inference.initialize(gameState)
        self.ghostBeliefs = [inf.getBeliefDistribution() for inf in self.inferenceModules]
        self.firstMove = True

    def observationFunction(self, gameState):
        "Removes the ghost states from the gameState"
        agents = gameState.data.agentStates
        gameState.data.agentStates = [agents[0]] + [None for i in range(1, len(agents))]
        return gameState

    def getAction(self, gameState):
        "Updates beliefs, then chooses an action based on updated beliefs."
        #for index, inf in enumerate(self.inferenceModules):
        #    if not self.firstMove and self.elapseTimeEnable:
        #        inf.elapseTime(gameState)
        #    self.firstMove = False
        #    if self.observeEnable:
        #        inf.observeState(gameState)
        #    self.ghostBeliefs[index] = inf.getBeliefDistribution()
        #self.display.updateDistributions(self.ghostBeliefs)
        return self.chooseAction(gameState)

    def chooseAction(self, gameState):
        "By default, a BustersAgent just stops.  This should be overridden."
        return Directions.STOP

class BustersKeyboardAgent(BustersAgent, KeyboardAgent):
    "An agent controlled by the keyboard that displays beliefs about ghost positions."

    def __init__(self, index = 0, inference = "KeyboardInference", ghostAgents = None):
        KeyboardAgent.__init__(self, index)
        BustersAgent.__init__(self, index, inference, ghostAgents)

    def getAction(self, gameState):
        return BustersAgent.getAction(self, gameState)

    def chooseAction(self, gameState):
        q = KeyboardAgent.getAction(self, gameState)
        return q

    def printLineData(self, gameState, mode=1):

        # Skip initial frames with the Stop direction
        if gameState.data.agentStates[0].getDirection() == "Stop": 
            return ""

        # Direccion al fantasma mas cercano
        is_at_north = False
        is_at_south = False
        is_at_east = False
        is_at_west = False

        nearest_ghost_index = gameState.data.ghostDistances.index(min(i for i in gameState.data.ghostDistances if i is not None))

        nearest_ghost_x_position = gameState.getGhostPositions()[nearest_ghost_index][0]
        nearest_ghost_y_position = gameState.getGhostPositions()[nearest_ghost_index][1]

        print("x -> " + str(nearest_ghost_x_position))
        print("y -> " + str(nearest_ghost_y_position))


        pacman_x_pos = gameState.getPacmanPosition()[0]
        pacman_y_pos = gameState.getPacmanPosition()[1]

        relative_x_pos = nearest_ghost_x_position - pacman_x_pos
        relative_y_pos = nearest_ghost_y_position - pacman_y_pos

        if relative_y_pos > 0:
            is_at_north = True
        if relative_y_pos < 0:
            is_at_south = True
        if relative_x_pos > 0:
            is_at_east = True
        if relative_x_pos < 0:
            is_at_west = True

        print("N -> " + str(is_at_north))
        print("S -> " + str(is_at_south))
        print("E -> " + str(is_at_east))
        print("W -> " + str(is_at_west))

        if mode == 1:

            return (

                str("North" in gameState.getLegalPacmanActions()) + # Can go North
                "," + str("South" in gameState.getLegalPacmanActions()) + # Can go South
                "," + str("East" in gameState.getLegalPacmanActions()) + # Can go East
                "," + str("West" in gameState.getLegalPacmanActions()) + # Can go West


                "," + str(is_at_north) + # Is at the north
                "," + str(is_at_south) + # Is at the south
                "," + str(is_at_east) + # Is at the east
                "," + str(is_at_west) + # Is at the west
        
                "," + str(gameState.data.agentStates[0].getDirection()) + # Actions by PacMan
                "\n" 

            )

        elif mode == 2:

            is_any_ghost_within_reach = (abs(relative_y_pos) == 1 and abs(relative_x_pos) == 0) or (abs(relative_y_pos) == 0 and abs(relative_x_pos) == 1)
            is_any_food_nearby = gameState.getDistanceNearestFood() == 1

            return (

                str(gameState.getScore()) + "\n" + # score

                str(is_any_ghost_within_reach) + # if there is a ghost nearby
                "," + str(is_any_food_nearby) + # if there is a dot to eat nearby

                "," + str(gameState.getScore()) + "," # scoreSiguiente

            )





from distanceCalculator import Distancer
from game import Actions
from game import Directions
import random, sys

'''Random PacMan Agent'''
class RandomPAgent(BustersAgent):

    def registerInitialState(self, gameState):
        BustersAgent.registerInitialState(self, gameState)
        self.distancer = Distancer(gameState.data.layout, False)
        
    ''' Example of counting something'''
    def countFood(self, gameState):
        food = 0
        for width in gameState.data.food:
            for height in width:
                if(height == True):
                    food = food + 1
        return food
    
    ''' Print the layout'''  
    def printGrid(self, gameState):
        table = ""
        ##print(gameState.data.layout) ## Print by terminal
        for x in range(gameState.data.layout.width):
            for y in range(gameState.data.layout.height):
                food, walls = gameState.data.food, gameState.data.layout.walls
                table = table + gameState.data._foodWallStr(food[x][y], walls[x][y]) + ","
        table = table[:-1]
        return table
        
    def chooseAction(self, gameState):
        move = Directions.STOP
        legal = gameState.getLegalActions(0) ##Legal position from the pacman
        move_random = random.randint(0, 3)
        if   ( move_random == 0 ) and Directions.WEST in legal:  move = Directions.WEST
        if   ( move_random == 1 ) and Directions.EAST in legal: move = Directions.EAST
        if   ( move_random == 2 ) and Directions.NORTH in legal:   move = Directions.NORTH
        if   ( move_random == 3 ) and Directions.SOUTH in legal: move = Directions.SOUTH
        return move


class WekaAgent(BustersAgent, KeyboardAgent):

    def __init__(self, index = 0, inference = "KeyboardInference", ghostAgents = None):
        KeyboardAgent.__init__(self, index)
        BustersAgent.__init__(self, index, inference, ghostAgents)

    def getAction(self, gameState):
        return BustersAgent.getAction(self, gameState)

    def chooseAction(self, gameState):  

        # Direccion al fantasma mas cercano
        is_at_north = False
        is_at_south = False
        is_at_east = False
        is_at_west = False

        nearest_ghost_index = gameState.data.ghostDistances.index(min(i for i in gameState.data.ghostDistances if i is not None))

        nearest_ghost_x_position = gameState.getGhostPositions()[nearest_ghost_index][0]
        nearest_ghost_y_position = gameState.getGhostPositions()[nearest_ghost_index][1]

        pacman_x_pos = gameState.getPacmanPosition()[0]
        pacman_y_pos = gameState.getPacmanPosition()[1]

        relative_x_pos = nearest_ghost_x_position - pacman_x_pos
        relative_y_pos = nearest_ghost_y_position - pacman_y_pos

        if relative_y_pos > 0:
            is_at_north = True
        if relative_y_pos < 0:
            is_at_south = True
        if relative_x_pos > 0:
            is_at_east = True
        if relative_x_pos < 0:
            is_at_west = True


        x = [
        str("North" in gameState.getLegalPacmanActions()),
        str("South" in gameState.getLegalPacmanActions()),
        str("East" in gameState.getLegalPacmanActions()),
        str("West" in gameState.getLegalPacmanActions()),
        str(is_at_north),
        str(is_at_south),
        str(is_at_east),
        str(is_at_west)
        ]
        print(x)
        import os
        wekapath = os.environ['WEKAPATH']
        move = self.weka.predict(wekapath + "/model.model", x, wekapath + "/data.arff", debug=False)
        print(move)
        return move


class GreedyBustersAgent(BustersAgent):
    "An agent that charges the closest ghost."

    def registerInitialState(self, gameState):
        "Pre-computes the distance between every two points."
        BustersAgent.registerInitialState(self, gameState)
        self.distancer = Distancer(gameState.data.layout, False)

    def chooseAction(self, gameState):
        """
        First computes the most likely position of each ghost that has
        not yet been captured, then chooses an action that brings
        Pacman closer to the closest ghost (according to mazeDistance!).

        To find the mazeDistance between any two positions, use:
          self.distancer.getDistance(pos1, pos2)

        To find the successor position of a position after an action:
          successorPosition = Actions.getSuccessor(position, action)

        livingGhostPositionDistributions, defined below, is a list of
        util.Counter objects equal to the position belief
        distributions for each of the ghosts that are still alive.  It
        is defined based on (these are implementation details about
        which you need not be concerned):

          1) gameState.getLivingGhosts(), a list of booleans, one for each
             agent, indicating whether or not the agent is alive.  Note
             that pacman is always agent 0, so the ghosts are agents 1,
             onwards (just as before).

          2) self.ghostBeliefs, the list of belief distributions for each
             of the ghosts (including ghosts that are not alive).  The
             indices into this list should be 1 less than indices into the
             gameState.getLivingGhosts() list.
        """
        pacmanPosition = gameState.getPacmanPosition()
        legal = [a for a in gameState.getLegalPacmanActions()]
        livingGhosts = gameState.getLivingGhosts()
        livingGhostPositionDistributions = \
            [beliefs for i, beliefs in enumerate(self.ghostBeliefs)
             if livingGhosts[i+1]]
        return Directions.EAST

class BasicAgentAA(BustersAgent):

    def registerInitialState(self, gameState):
        BustersAgent.registerInitialState(self, gameState)
        self.distancer = Distancer(gameState.data.layout, False)
        self.countActions = 0
        
    ''' Example of counting something'''
    def countFood(self, gameState):
        food = 0
        for width in gameState.data.food:
            for height in width:
                if(height == True):
                    food = food + 1
        return food
    
    ''' Print the layout'''  
    def printGrid(self, gameState):
        table = ""
        #print(gameState.data.layout) ## Print by terminal
        for x in range(gameState.data.layout.width):
            for y in range(gameState.data.layout.height):
                food, walls = gameState.data.food, gameState.data.layout.walls
                table = table + gameState.data._foodWallStr(food[x][y], walls[x][y]) + ","
        table = table[:-1]
        return table

    def printInfo(self, gameState):
        print("---------------- TICK ", self.countActions, " --------------------------")
        # Map size
        width, height = gameState.data.layout.width, gameState.data.layout.height
        print("Width: ", width, " Height: ", height)
        # Pacman position
        print("Pacman position: ", gameState.getPacmanPosition())
        # Legal actions for Pacman in current position
        print("Legal actions: ", gameState.getLegalPacmanActions())
        # Pacman direction
        print("Pacman direction: ", gameState.data.agentStates[0].getDirection())
        # Number of ghosts
        print("Number of ghosts: ", gameState.getNumAgents() - 1)
        # Alive ghosts (index 0 corresponds to Pacman and is always false)
        print("Living ghosts: ", gameState.getLivingGhosts())
        # Ghosts positions
        print("Ghosts positions: ", gameState.getGhostPositions())
        # Ghosts directions
        print("Ghosts directions: ", [gameState.getGhostDirections().get(i) for i in range(0, gameState.getNumAgents() - 1)])
        # Manhattan distance to ghosts
        print("Ghosts distances: ", gameState.data.ghostDistances)
        # Pending pac dots
        print("Pac dots: ", gameState.getNumFood())
        # Manhattan distance to the closest pac dot
        print("Distance nearest pac dots: ", gameState.getDistanceNearestFood())
        # Map walls
        print("Map:")
        print( gameState.getWalls())
        # Score
        print("Score: ", gameState.getScore())
        
    def printLineData(self, gameState, mode=1):

        # Skip initial frames with the Stop direction
        if gameState.data.agentStates[0].getDirection() == "Stop": 
            return ""

        # Direccion al fantasma mas cercano
        is_at_north = False
        is_at_south = False
        is_at_east = False
        is_at_west = False

        nearest_ghost_index = gameState.data.ghostDistances.index(min(i for i in gameState.data.ghostDistances if i is not None))

        nearest_ghost_x_position = gameState.getGhostPositions()[nearest_ghost_index][0]
        nearest_ghost_y_position = gameState.getGhostPositions()[nearest_ghost_index][1]

        print("x -> " + str(nearest_ghost_x_position))
        print("y -> " + str(nearest_ghost_y_position))


        pacman_x_pos = gameState.getPacmanPosition()[0]
        pacman_y_pos = gameState.getPacmanPosition()[1]

        relative_x_pos = nearest_ghost_x_position - pacman_x_pos
        relative_y_pos = nearest_ghost_y_position - pacman_y_pos

        if relative_y_pos > 0:
            is_at_north = True
        if relative_y_pos < 0:
            is_at_south = True
        if relative_x_pos > 0:
            is_at_east = True
        if relative_x_pos < 0:
            is_at_west = True

        print("N -> " + str(is_at_north))
        print("S -> " + str(is_at_south))
        print("E -> " + str(is_at_east))
        print("W -> " + str(is_at_west))

        if mode == 1:

            return (

                str("North" in gameState.getLegalPacmanActions()) + # Can go North
                "," + str("South" in gameState.getLegalPacmanActions()) + # Can go South
                "," + str("East" in gameState.getLegalPacmanActions()) + # Can go East
                "," + str("West" in gameState.getLegalPacmanActions()) + # Can go West


                "," + str(is_at_north) + # Is at the north
                "," + str(is_at_south) + # Is at the south
                "," + str(is_at_east) + # Is at the east
                "," + str(is_at_west) + # Is at the west
        
                "," + str(gameState.data.agentStates[0].getDirection()) + # Actions by PacMan
                "\n" 

            )

        elif mode == 2:

            is_any_ghost_within_reach = (abs(relative_y_pos) == 1 and abs(relative_x_pos) == 0) or (abs(relative_y_pos) == 0 and abs(relative_x_pos) == 1)
            is_any_food_nearby = gameState.getDistanceNearestFood() == 1

            return (

                str(gameState.getScore()) + "\n" + # score

                str(is_any_ghost_within_reach) + # if there is a ghost nearby
                "," + str(is_any_food_nearby) + # if there is a dot to eat nearby

                "," + str(gameState.getScore()) + "," # scoreSiguiente

            )

    def chooseAction(self, gameState):
        self.countActions = self.countActions + 1
        self.printInfo(gameState)
        move = Directions.STOP
        legal = gameState.getLegalActions(0) ##Legal position from the pacman+

        distancer = Distancer(gameState.data.layout)


        # Move towards the nearest ghost

        pos_pacman = gameState.getPacmanPosition()
        ghost_to_follow = 0
        nearest_distance = 999999999999999

        # Look which ghost is closer
        for i in range(0, len(gameState.getGhostPositions())):
            distance_to_analyze = distancer.getDistance((pos_pacman[0], pos_pacman[1]),(gameState.getGhostPositions()[i][0], gameState.getGhostPositions()[i][1]))
            if gameState.getLivingGhosts()[i+1] and distance_to_analyze < nearest_distance:
                ghost_to_follow = i
                nearest_distance = distance_to_analyze

        # Look how to approach the ghost
        valid_directions = legal
        if "Stop" in valid_directions:
            valid_directions.remove("Stop")
        
        # Analyze which direction is better
        current_best_distance = 99999999999999
        current_direction = None

        for direction in valid_directions:
            pacman_position = (pos_pacman[0], pos_pacman[1])

            if direction is Directions.NORTH:
                pacman_position = (pos_pacman[0], pos_pacman[1] + 1)
            elif direction is Directions.SOUTH:
                pacman_position = (pos_pacman[0], pos_pacman[1] - 1)   
            elif direction is Directions.WEST:
                pacman_position = (pos_pacman[0] - 1, pos_pacman[1])               
            elif direction is Directions.EAST:
                pacman_position = (pos_pacman[0] + 1, pos_pacman[1])   
            
            resulting_distance = distancer.getDistance(pacman_position,
                (gameState.getGhostPositions()[ghost_to_follow][0], gameState.getGhostPositions()[ghost_to_follow][1]))

            if resulting_distance < current_best_distance:
                current_direction = direction
                current_best_distance = resulting_distance

        return current_direction





