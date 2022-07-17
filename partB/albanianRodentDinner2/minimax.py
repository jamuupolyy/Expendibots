import math
import copy
import numpy as np

from albanianRodentDinner.hashtable import *
from albanianRodentDinner.entities import *
from albanianRodentDinner.heuristic import *
from albanianRodentDinner.moves import *

# The max depth of the minimax tree we aim to explore until
value_limit = {WHITE: -math.inf, BLACK: math.inf}






# Just a dummy function to symbolise terminal test
def terminal_node_test(board):
    return None


# Minimax algorithm with alpha beta pruning
def minimax_ab(board, alpha, beta, colour, depth, prev_move):
    """
    Implements minimax with alpha beta pruning
    :param board: a current board state
    :param alpha:
    :param beta:
    :param colour: if the current player wants to maximise or minimise the action.
    :param depth: the current depth in a tree
    :param prev_move:
    :return
    """

    # The initial call to this function should be something like:
    #   minimax_ab(board, depth, -math.inf, math.inf, TRUE)

    # Terminal node or depth == 0
    # original = if '''terminal_node_test(board) or '''depth == 0:
    
    value = value_limit[colour]
    blown_up = False
    broken = False
    best_move = None

    

    # Bottom level, we initialise the minimax values for each leaf node
    if depth == 0:
        # Should return evaluation value
        return (evaluation_control(board,colour,1,1),None)
    
    # for loop for number of pieces to mov e
    for key in list(board.dict):
        #print(key)
       
        if board.dict[key].team == colour:
            
            
            for move in MOVES:

                for index in range(1, board.dict[key].count + 1):

                    if (blown_up == False):

                        base = board.dict[key].count + 1
                  
                    else:
                        base = board.dict[key].count
                      
                    # for loop for number steps to move
                    for step in range(base,0,-1):
                        if (is_legal_move(key, scale_vector(move, step), board, colour)) or blown_up == False:
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
                            
                            if (blown_up == True):

                                simulate_move(key, move, index, board, board.dict[key].count, step, colour)
                            else:
                                board.boom(key)
                                blown_up = True

                                

                            
                     
                            
                            
                            if colour == WHITE: 
                                value = max(value,minimax_ab(board, alpha, beta, inverse_color[colour], depth - 1, move)[0])
                                if value > alpha:
                                    best_move = (key, index, step)
                                alpha = max(alpha, value)
                                
                                if alpha >= beta:
                                    board = copy.deepcopy(old_board)
                                    break
                                

                            else:
                                value = min(value,minimax_ab(board, alpha, beta, inverse_color[colour], depth - 1, move)[0])
                                if value < beta:
                                    best_move = (key, index, step)
                                beta = min(beta, value)
                                
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
    return value, best_move


def minimax_heuristic():
    return 0


def minimax_control(board, alpha, beta, colour, depth, prev_move):
    """
    Implements contorl loop for minimax with alpha beta pruning
    :param board: a current board state
    :param depth: the current depth in a tree
    :param colour: if the current player wants to maximise or minimise the action.
    :return
    """
    print("########################")
    #hash_table = np.zeros((8,8,32))
    #init_table(hash_table)
    
    #hash_val = compute_hash(board, hash_table)
    #print(hash_val)

    print("########################")
    return(minimax_ab(board, alpha, beta, colour, depth, prev_move))