from queue import PriorityQueue
import copy
import sys
from albanianRodentDinner.moves import *
from albanianRodentDinner.group import *
from albanianRodentDinner.entities import *

# Records the lowest threshold encountered at the end of each a* iteration at a certain threshold
GLOBAL_THRESHOLD = sys.maxsize

VISITED = []


def ida_star_control_loop(board, key, group, intersection_flag, colour):
    """
    Controls the threshold to call ida at
    :param colour:
    :param board: contains board data
    :param key: key of piece we are moving
    :param group: group or intersection to head towards
    :param intersection_flag: flag indiicating if we are trying to reach an intersection
    """
    global GLOBAL_THRESHOLD
    global VISITED

    # starts out as false and returns with True when the solution is found
    found = False
    # calculates the initial f value for the initial board (purely based on heuristic)
    board.f = threshold = manhattan_heuristic(
        board, key, group, intersection_flag)

    # Initial threshold generated from heuristic
    while not found:
        found = copy.deepcopy(ida_star(board, key, group, threshold, None, intersection_flag, colour))
        threshold = GLOBAL_THRESHOLD

    # clear the global visited list, begin again
    VISITED.clear()
    return found


def ida_star(board, key, group, threshold, prev_move, intersection_flag, colour):
    """
    Controls the threshold to call ida at
    :param visited:
    :param colour:
    :param board: contains board data
    :param key: key of piece we are moving
    :param group: group or intersection to head towards
    :param threshold: determines the max threshold of nodes to be explored in each iteration
    :param prev_move: records the previous move
    :param intersection_flag: flag indicating 1 if we are trying to reach an intersection, or 2 if we
    want to reach a single piece.
    """
    global GLOBAL_THRESHOLD
    found = False

    # for loop for each move
    for move in MOVES:
        move_index = False

        # for loop for number of pieces to move
        for i in range(board.dict[key].count, 0, -1):

            # for loop for number steps to move
            for step in range(board.dict[key].count, 0, -1):

                # checks if move is legal
                if is_legal_move(key, scale_vector(move, step), board, colour):
                    move_index = i

                # ensures that a piece doesn't backtrack
                if move != inverse_move[prev_move] and move_index != False and \
                        is_legal_move(key, scale_vector(move, step), board, colour):

                    # moves a piece and records the future position of the piece
                    future_position = move_piece(key, move, move_index, board, board.dict[key].count, step, colour)

                    # updates the total of moves made by the board
                    board.g += move_index

                    # appends a move to the commands list
                    VISITED.append(("MOVE", move_index, key, future_position))

                    # calculates the heuristic of the board
                    heuristic = manhattan_heuristic(board,
                                                    future_position,
                                                    group,
                                                    intersection_flag)

                    # calculates the f function of the board
                    board.f = board.g + heuristic

                    # if the f score for the current board is above the threshold
                    # the global threshold is updated to keep track of the next lowest
                    # threshold to explore in the next iteration of the ida_star_control_loop
                    if board.f > threshold:

                        # condition for the first threshold check when global threshold will always
                        # be lower than the f value of a board
                        if threshold == GLOBAL_THRESHOLD:
                            GLOBAL_THRESHOLD = board.f

                        else:
                            GLOBAL_THRESHOLD = min(board.f, GLOBAL_THRESHOLD)

                    # if the f score of the current board is below the current threshold, it is explored
                    else:

                        # if a group or intersection is being investigated
                        # and the heuristic value is 0 and there are no surrounding pieces, blow up
                        if heuristic == 0:
                            # adds boom to command list
                            VISITED.append(("BOOM", future_position))

                            return VISITED

                        # calls the next round of ida_star based on the new board state
                        found = ida_star(board, future_position, group, threshold, move, intersection_flag, colour)

                        # if found is called then we return it (contains movement commands if not false)
                        if found != False:
                            return found

                    # at the end of the iteration, the board is returned to the state
                    # before the current move was made by undoing it, allowing for the
                    # exploration of other moves
                    move_piece(future_position, inverse_move[move], move_index, board,
                               board.dict[future_position].count, step, colour)

                    # removes a move command when we undo a step
                    VISITED.pop()

                    # the steps made earlier are undone
                    board.g -= move_index
    return False
