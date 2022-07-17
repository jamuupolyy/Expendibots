import math
import random
import numpy as np

from albanianRodentDinner.moves import *
from albanianRodentDinner.group import find_bridges
from albanianRodentDinner.entities import Board


# Maximum number of pieces one player could have
MAX_N = 12

# We want to implement the following heuristics:
#   -   defensive - last 5 seconds, try and get away
#   -   sniper strategy - combination of multiple stacks, keeping larger stacks closer to our side
#                         and shooting stacks further
#   -   projecting the radius of pieces being shot out (D)


def evaluation_control(board, offense_weight, defensive_weight ):

    # return f = w_i*x_i, where w are the weights and x are the features
    value = 0  

    value += baseline(board)
    #value += isolation(board,color)
    value += random.randint(-10, 10)
    #print(value)
    return value


def sniper(board):
    """
    Sniper strategy works as follows:
        - promote formation of larger stacks
        - keep larger stacks closer to side of the board
        - larger stacks fire pieces out across board
        - blow up when advantageous to do so

    :param board: the current board
    :param colour: player colour
    :return: an evaluation value
    """
    f = baseline(board) + \
        multiple_stacks(board) + \
        split_board(board)

    return f


def defensive(board):
    """
    Composite function to promote playing defensive by keeping as many pieces alive
    and as far away from enemy as possible. Blow-up if absolutely necessary.
    :param board: the current board
    :param colour: the player's colour
    :return: a weighted sum of heuristic values
    """
    f = np.array([1.5, 1.5]) * baseline(board) + \
        np.array([0.2, 0.2]) * isolation(board)

    return f


def baseline(board):
    """
    Baseline evaluation function.
    Utilitarian, only tries to maximise absolute piece count.
    F = # player pieces - # enemy pieces
    :param board:
    :param colour: binary value. which team the player controls
    :return: numpy array with [white_eval, black_eval]
    """
    white = board.get_white_pieces()
    black = board.get_black_pieces()

    value = sum(piece.get_count() for piece in white.values()) - \
        sum(piece.get_count() for piece in black.values())

    return np.array([value, -value])


def blow_the_bridge(board):
    """
    count number of bridges.
    # enemy bridges
    Create bridges which an enemy player and move into to blow up 2+ pieces.
    :param board:
    :return:
    """
    white_group_set = board.get_white_group_set()
    black_group_set = board.get_black_group_set()
    group_sets = [white_group_set, black_group_set]

    return np.array([len(find_bridges(group_set)) for group_set in group_sets])


def multiple_stacks(board):
    """
    Return a weighted sum from stacks of pieces,
        where f = sum(c^2 / 12) for all c > 1 in pieces, where c is the number of pieces in each teams stack.
    This evaluation function is designed to promote having larger stacks of pieces.
    :param board:
    :param colour: binary value. which team the player controls
    :return:
    """
    global MAX_N

    white_value = sum(math.pow(piece.get_count(), 2) / MAX_N for piece in board.get_white_pieces()
                      if piece.get_count() > 1)
    black_value = sum(math.pow(piece.get_count(), 2)/MAX_N for piece in board.get_black_pieces()
                      if piece.get_count() > 1)

    return np.array(white_value, black_value)


def isolation(board):
    """
    Tries to keep pieces alive and as far as possible from the opponent, with higher weight pieces being
    weighted more heavily for staying away.
    f = sum(min manhattan distances between players and each stack in an opponents group)*product(sqrt(size of stacks))

    :param board:
    :param colour:
    :return: np.array in form [white_iso_value, black_iso_value]
    """
    stacks = [board.get_white_pieces(), board.get_black_pieces()]
    opp_group_sets = [board.get_black_group_set(), board.get_white_group_set()]

    # Initialise np array to hold all distance scores
    evaluation_array = np.array([])
    for stack, opp_group_set in zip(stacks, opp_group_sets):
        iso_score = 0
        for key, val in zip(stack.keys(), stack.values()):

            for opp_group in opp_group_set:

                # opp_stacks are of the form [count, x_coord, y_coord]. index accordingly
                iso_score += min([manhattan_distance(key, opp_stack[1:3]) for opp_stack in opp_group])

            iso_score *= math.sqrt(val.get_count())

        evaluation_array = np.append(evaluation_array, [iso_score])

    return evaluation_array


def split_board(board):
    """
    Split the board and weight stacks that are closer to their end of the board more heavily.
    This is done by summing the row number and multiplying by the number of pieces in a stack,
        then taking the inverse of the score.
    :param board:
    :param colour:
    :return:
    """
    white_stacks = board.get_white_pieces()
    black_stacks = board.get_black_pieces()
    player_stacks = {1: white_stacks, 0: black_stacks}

    evaluation_array = np.array([])
    for colour_key, stacks in zip(player_stacks.keys(), player_stacks.values()):
        split_value = 0
        for key, val in zip(stacks.keys(), stacks.values()):
            split_value += (key[1] if colour_key else 7-key[1]) * val.get_count()

        # Just give it a very large number if at the end
        split_score = 10 if split_value == 0 else 1.0/split_value
        evaluation_array = np.append(evaluation_array, split_score)

    return evaluation_array


def eucledean_distance(a, b):
    '''
    Calculate eucledean distance between two positions.
    :param a: position a
    :param b: position b
    :return: the eucledean distance between a and b.
    '''
    distance = math.sqrt(((a[0] - b[0]) ** 2) + ((a[1] - b[1]) ** 2))
    return distance


def group_manhattan_distance(a, b):
    """
    Calculate manhattan distance between two positions for groups.
    :param a: position a
    :param b: position b
    :return: the manhattan distance between a and b.
    """

    x = math.fabs(a[0] - b[0])
    y = math.fabs(a[1] - b[1])
    # detects if white piece is in the corner of goal piece
    if (x == 1 and y == 1):
        return 1
    return x + y


def manhattan_distance(a, b):
    """
    Calculate manhattan distance between two positions.
    :param a: position a
    :param b: position b
    :return: the manhattan distance between a and b.
    """
    return math.fabs(a[0] - b[0]) + math.fabs(a[1] - b[1])


def manhattan_heuristic(board, primary_piece, group, intersection_flag):
    """
    Heuristic function to guide search in an appropriate direction.
    :param primary_piece:
    :param group:
    :param intersection_flag: whether there is an intersection, or 2 for a single piece in usage for greedy algorithm.
    :return: the manhattan distance between a piece and the intersection or nearest group black stack
    """
    if intersection_flag == 1:
        return manhattan_distance(primary_piece, group)

    if intersection_flag == 2:
        return manhattan_distance(primary_piece, group) - 1

    # Initialise the minimum value to infinity, we aim to improve this
    min_value = math.inf
    goal = None
    goal_pos = None
    for black_stack in group:
        # print(group)
        # Get the co-ordinates of the black stack
        black_stack_position = black_stack[1], black_stack[2]
        # Iterate through each stack of white pieces
        # Calculate the manhattan distance
        distance = eucledean_distance(
            primary_piece, black_stack_position)
        # If the calculated manhattan distance is less than the current minimum, replace it.
        if distance < min_value:
            min_value = distance
            goal = black_stack
            goal_pos = black_stack_position

    return group_manhattan_distance(primary_piece, goal_pos) - 1
