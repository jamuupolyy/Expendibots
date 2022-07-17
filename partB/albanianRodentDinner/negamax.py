
import math
import copy
import numpy as np

from albanianRodentDinner.entities import *
from albanianRodentDinner.heuristic import *
from albanianRodentDinner.moves import *
from albanianRodentDinner.hashtable import *

# The max depth of the negamax tree we aim to explore until
DEPTH_LIMIT = 2

# Just a dummy function to symbolise terminal test
def terminal_node_test(board):
    return None


# Negamax algorithm with alpha beta pruning
def negamax_ab(player, board, alpha, beta, colour, depth, prev_move, hash_table,prior_hash):
    """
    Implements negamax with alpha beta pruning
    :param board: a current board state
    :param depth: the current depth in a tree
    :param colour: if the current player wants to maximise or minimise the action.
    :return
    """

    # The initial call to this function should be something like:
    #   negamax_ab(board, depth, -math.inf, math.inf, TRUE)

    # Terminal node or depth == 0
    # original = if '''terminal_node_test(board) or '''depth == 0:
    value = -math.inf
    blown_up = False
    boom = False
    broken = False
    best_move = None

    if depth == 0:
        # Should return evaluation value
        adj_factor = 1 if DEPTH_LIMIT % 2 == 0 else -1

        value = defensive(board)

        # choose value depending on which team you are
        colour_value = value[0] if colour else value[1]

        return colour_value * adj_factor, best_move, [x * adj_factor for x in value]

    # for loop for number of pieces to move
    for key in list(board.dict):
        if board.dict[key].team == colour:

            for move in MOVES:

                for index in range(1, board.dict[key].count + 1):
                    #if we have not blown up the piece yet, we will add an extra step
                    #to signify that we need to blow up
                    if (blown_up == False):
                        base = board.dict[key].count + 1
                    else:
                        base = board.dict[key].count


                    # for loop for number steps to move, +1 if we still need to blow up
                    for step in range(base,0,-1):
                        if (is_legal_move(key, scale_vector(move, step), board, colour)) or blown_up == False:
                            #resets the hash value to the value given in the call to the function
                            hash_val = prior_hash
                            '''
                            print("#############################")
                            print("key = "+ str(key))
                            print("move = "+ str(move))
                            print("index = "+ str(index))
                            print("step = "+ str(step))
                            print("depth = "+ str(depth))
                            print("base = "+str(base))
                            if blown_up == False:
                                print("BLOW UP")
                            print("#############################")
                            '''

                            old_board = copy.deepcopy(board)
                            
                            #executes normal move if not blow up
                            if (blown_up == True):
                                hash_moves = simulate_move(key, move, index, board, board.dict[key].count, step, colour)
                                #computes hash of moving
                                hash_val = compute_move_hash(board, hash_val, hash_table, hash_moves[0],  hash_moves[1],  hash_moves[2],  hash_moves[3],  hash_moves[4],  hash_moves[5])
                            else:
                                #print("BLOW UP")
                                exploded = board.boom(key)
                                blown_up = True
                                hash_val = compute_boom_hash(board, hash_val, hash_table, exploded)
                                #board.print()
                                #print(hash_val,"-----",depth,"-----",key)
                                boom = True

                            #checks if hash has been recorded, if it has it is assigned the pre-computed value
                            if hash_val in player.hash_dict.keys():
                                value = player.hash_dict[hash_val][0] if colour else player.hash_dict[hash_val][1]
                                
                                #board.print()
                                #print(hash_val,"-----",depth,"-----",key,'-----',player.hash_dict[hash_val])
                            
                            #calls minimax if a new hash is recorded
                            else:
                                result = negamax_ab(player, board, -beta, -alpha, inverse_color[colour], depth - 1, move, hash_table,hash_val)
                                original_value = -result[0]
                                value = max(value,original_value)
                                #tracks the newly computed value and assigns it to a hash in a dictionary
                                if result[2]!=None:

                                    player.hash_dict[hash_val] = [x * -1 for x in result[2]]
                            
                            if value > alpha:
                                best_move = (key, index, step, move, boom)
                                    
                            boom = False
                            alpha = max(alpha, value)

                            if alpha >= beta:
                                board = copy.deepcopy(old_board)
                                broken = True
                                break

                            board = copy.deepcopy(old_board)
                    if broken:
                        break
                if broken:
                    break
            if broken:
                break
        blown_up = False           
    return (value, best_move, None)


def negamax_heuristic():
    return 0


def negamax_control(player,board, hash_table, alpha, beta, colour, depth, prev_move):
    """
    Implements contorl loop for minimax with alpha beta pruning
    :param board: a current board state
    :param depth: the current depth in a tree
    :param colour: if the current player wants to maximise or minimise the action.
    :return
    """
    hash_val = compute_hash(board, hash_table)
    return(negamax_ab(player,board, alpha, beta, colour, depth, prev_move,hash_table, hash_val))
