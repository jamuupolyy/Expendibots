from albanianRodentDinner.IDA import ida_star_control_loop
from albanianRodentDinner.minimax import *
from albanianRodentDinner.negamax import *
from albanianRodentDinner.group import *
import numpy
import time

# Initialise some global variables
COLOR = None
DEPTH_LIMIT = 2


class ExamplePlayer:
    def __init__(self, colour):
        self.hash_dict = {}
        self.hash_lookup =  np.zeros((8,8,32))
        self.timer = 0
        self.colour_int = 1 if colour == "white" else 0
        self.board = Board()
        """
        This method is called once at the beginning of the game to initialise
        your player. You should use this opportunity to set up your own internal
        representation of the game state, and any other information about the 
        game state you would like to maintain for the duration of the game.

        The parameter colour will be a string representing the player your 
        program will play as (White or Black). The value will be one of the 
        strings "white" or "black" correspondingly.
        """
        # TODO: Set up state representation.
        COLOR = colour

        data = {
            "white": [[1,0,0],[1,0,1],[1,1,0],[1,1,1],[1,3,0],[1,3,1],[1,4,0],[1,4,1],[1,6,0],[1,6,1],[1,7,0],[1,7,1]],
            "black": [[1,0,6],[1,0,7],[1,1,6],[1,1,7],[1,3,6],[1,3,7],[1,4,6],[1,4,7],[1,6,6],[1,6,7],[1,7,6],[1,7,7]]
         }

        black_group_set = group_pieces(data, self.board, 'black')
        white_group_set = group_pieces(data, self.board, 'white')

        init_table(self.hash_lookup)

        # registers groups and pieces into a board class instance
        self.board.register_data(black_group_set, white_group_set, data)

    def action(self):
        """
        This method is called at the beginning of each of your turns to request 
        a choice of action from your program.

        Based on the current state of the game, your player should select and 
        return an allowed action to play on this turn. The action must be
        represented based on the spec's instructions for representing actions.
        """

        start = time.process_time()

        # We're in the end game now
        if self.timer > 55:

            # if we are winning by a small margin, play defensively
            if 0 < self.advantage_check() <= 2:
                "Play smart bois"

            # if we are winning by large margin or losing by a small one, can play normally
            elif -2 <= self.advantage_check() < 0 or self.advantage_check() > 2:
                "Play normally"

            # if we are losing by large margin, suicide squad shit
            elif self.advantage_check() < -2:
                move = self.get_greedy()
                return move

        # just hiding here for now
        else:
            old_board = copy.deepcopy(self.get_board())
            res = negamax_control(self,self.get_board(),self.get_hash_lookup() ,-math.inf, math.inf, self.colour_int, DEPTH_LIMIT, None)
            self.set_board(copy.deepcopy(old_board))
            move = res[1]
            end = time.process_time()
            print("TIME: " + str(end - start))
            #print(self.hash_dict)
            #return ("BOOM", (3, 3))
            self.update_timer(time.process_time() - start)

            if not move[4]:
                return 'MOVE', move[1], move[0], add_vectors(move[0], scale_vector(move[3], move[2]))
            else:
                return "BOOM", move[0]

        #############################################
        #END TESTING FOR MINIMAX
        # TODO: Decide what action to take, and return it

    def update(self, colour, action):
        """
        This method is called at the end of every turn (including your player’s 
        turns) to inform your player about the most recent action. You should 
        use this opportunity to maintain your internal representation of the 
        game state and any other information about the game you are storing.

        The parameter colour will be a string representing the player whose turn
        it is (White or Black). The value will be one of the strings "white" or
        "black" correspondingly.

        The parameter action is a representation of the most recent action
        conforming to the spec's instructions for representing actions.

        You may assume that action will always correspond to an allowed action 
        for the player colour (your method does not need to validate the action
        against the game rules).
        """
        print("action -= " + str(action))

        if colour == "white":
            if action[0] == "MOVE":
                self.board.move_white_piece(action[2],action[3],action[1],None)
            else:
                self.board.boom(action[1])
        else:
            if action[0] == "MOVE":
                self.board.move_black_piece(action[2],action[3],action[1],None)
            else:
                self.board.boom(action[1])
        # TODO: Update state representation in response to action.

    def update_timer(self, seconds):
        self.timer += seconds

    def get_greedy(self):
        """
        Greedy action to path-find to closest opponent piece and blow it up.
        Reuse of part A code.
        :return:
        """
        colour = 1 if COLOR == "white" else 0

        player_piece, opp_piece = find_closest_pieces(self.get_board(), colour)
        print(player_piece, opp_piece)

        # call IDA and return the first move of the stack
        old_board = copy.deepcopy(self.get_board())
        first_move = ida_star_control_loop(self.get_board(), player_piece, opp_piece, 2, colour).pop()
        self.set_board(copy.deepcopy(old_board))
        return first_move

    def advantage_check(self):
        """
        Check how many pieces we are either winning or losing by.
        :return:
        """
        colour = 1 if COLOR == "white" else 0
        opp_colour = 0 if COLOR == "white" else 1

        return baseline(self.board, colour)

    def get_board(self):
        return self.board

    def set_board(self, new_board):
        self.board = new_board
    
    def get_hash_lookup(self):
        return self.hash_lookup

    def set_board_hash_lookup(self, hash_lookup):
        self.hash_lookup = hash_lookup