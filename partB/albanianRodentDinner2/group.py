import math
import copy

from albanianRodentDinner.moves import *
from albanianRodentDinner.heuristic import *


def assign_bridges(board, bridges):
    """
    Assign white pieces to bridges based on distance.
    :param board: contains board data
    :param board: contains bridge co ordinates
    :return: key which should be used to get to intersection
    """
    curr_bridge = False
    primary_key = False
    min_value = math.inf
    for bridge in bridges:
        for key in board.white_dict:
            distance = eucledean_distance(key, bridge)
            if distance < min_value:
                min_value = distance
                primary_key = key
                curr_bridge = bridge
    return (primary_key, curr_bridge)


def assign_pieces(board):
    """
    Assign white pieces to black groups based on distance.
    :param board: contains board data
    :return: assigned pieces per group
    """
    if (board.group_set == []):
        return False

    group_set = board.get_group_set()
    if (group_pieces == []):
        return
    white_stacks = board.get_white_pieces()
    white_pieces = []
    for stack in white_stacks:
        for _count in range(0, white_stacks[stack].count):
            white_pieces.append((stack, white_stacks[stack]))

    # All assignments are indexed by white piece
    assignments = list()

    # Iterate through all white stacks
    for white_stack in white_pieces:

        white_piece = white_stack[0]

        # List of groups with their corresponding distances to the current white stack
        distance_to_groups = list()

        # Iterate through all groups in the group set, and order the distances between white stacks and groups.
        for group in group_set:

            min_value = math.inf

            for black_stack in group:
                black_stack_position = black_stack[1], black_stack[2]

                distance = eucledean_distance(
                    white_piece, black_stack_position)

                if distance < min_value:
                    min_value = distance

            distance_to_groups.append((min_value, group))

        # Order the stacks
        ordered_stacks = sorted(distance_to_groups, key=lambda x: x[0])

        # Value to assign
        to_assign = ordered_stacks.pop(0)[1]

        # If an assignment has already been made, get the next closest group to assign to the white stack.
        for assignment in assignments:

            # Get the assignment group from the assignment list
            assignment_group = assignment[1]

            # If the current assignment has already been assigned, get the next one.
            if to_assign == assignment_group and len(ordered_stacks) > 0:
                to_assign = ordered_stacks.pop(0)[1]

        assignments.append((white_piece, to_assign))

    return assignments


def group_pieces(data, board, color):
    """
    Returns groups of pieces that can blow up each other
    :param data: dictionary containing info about black and white pieces
    :param board: the current board
    :return: a list of lists grouped by black pieces that can blow up each other
    """
    pieces = data[color]
    visited = []
    group = []
    group_set = []

    # iterates through each piece
    for piece in pieces:

        # only searches the surroundings of a piece if it has not been visited
        if piece not in visited:
            search_surroundings(piece, visited, pieces, group, board)

            # when the function returns, a group has been found and will be added to a group of sets
            group_set.append(group)

            # group variable is reset to determine the next group of pieces
            group = []

    return group_set


def find_closest_pieces(board, colour):
    """
    Find the closest two pieces between the player and the opponent.
    :param board: the current board
    :param colour: the players colour
    :return: a tuple containing the player piece and the opponent piece that are closest to each other.
    """
    pieces = board.get_white_pieces() if colour else board.get_black_pieces()
    opponent_pieces = board.get_black_pieces() if colour else board.get_white_pieces()

    min_val = math.inf
    current_player_piece = None
    current_opp_piece = None
    for player_piece in pieces:
        for opp_piece in opponent_pieces:

            distance = manhattan_distance(player_piece, opp_piece)
            if distance < min_val:
                min_val = distance
                current_player_piece = player_piece
                current_opp_piece = opp_piece

    return current_player_piece, current_opp_piece


# DEPRECATED
def get_to_safety(board, boom_location, piece_to_move):
    """
    Detects white pieces that are in blast radius, and tries to find a safe place for them to move to.
    If no such place exists, cya buddy.
    :param board: the current board
    :param boom_location: the location of the boom
    :param piece_to_move: the piece which needs to move out of the blast radius
    :return:
    """

    # Get all pieces of the dictionary, and initialise a set to hold all possible blast points
    affected_pieces = board.simulate_boom(boom_location)
    all_board_pieces = set(board.get_dict().keys())
    blast_points = set()

    # Iterate through all stacks on the board
    for stack in affected_pieces:

        # Iterate through all possible neighbouring points
        for search_move in SEARCH_MOVES:

            blast_point = add_vectors(stack, search_move)

            # If the addition of vectors results in a position that is NOT outside the board,
            # add it to the blast points.
            if validate_bounds_of_board(blast_point):
                blast_points.add(blast_point)

    # Get a set of "safe" points, where a blast cannot explode pieces here.
    safe_points = all_possible_board_positions().difference(
        all_board_pieces).difference(blast_points)

    # No safe points, say good bye
    if len(safe_points) == 0:
        return False

    # Iterate through all safe points, and find the closest safe point to the primary white piece.
    closest_point = None
    min_value = math.inf
    for safe_point in safe_points:
        distance = manhattan_distance(piece_to_move, safe_point)
        if distance < min_value:
            min_value = distance
            closest_point = safe_point

    return closest_point


def find_bridges(group_set):
    """
    Find all co-ordinates for each group of groups which can be linked by the presence of a white piece.
    We first find the neighbouring co-ordinates for each black stack, then set difference between groups
        to find overlapping co-ordinates.
    :param group_set:
    :return:
    """

    # This will hold sets of co-ordinates.
    all_groups_neighbours = list()

    # Iterate through the group_set and apply all SEARCH_MOVES to find all neighbouring co-ordinates
    #   for each black stack within one block.
    for group in group_set:

        stack_neighbour_coordinates = set()

        # Get the co-ordinates of the stack
        for stack in group:
            stack_coordinates = stack[1], stack[2]

            # Go through all moves
            for search_move in SEARCH_MOVES:
                stack_neighbour_coordinates.add(
                    add_vectors(stack_coordinates, search_move))

        all_groups_neighbours.append(stack_neighbour_coordinates)

    # Make a copy of the neighbours to iterate through and find overlapping areas
    overlaps = set()
    queue = copy.deepcopy(all_groups_neighbours)

    # While the queue is not empty, pop the first set of co-ordinates
    while len(queue) > 0:
        group = queue.pop(0)

        # Go through all other groups still in the queue and find all possible intersecting points
        # Note: we don't look for intersecting points between stacks in their own groups, as by definition
        #   of a group they will intersect.
        for other_groups in queue:
            out_of_bounds_points = set()
            possible_bridges = group.intersection(other_groups)

            for point in possible_bridges:

                # Point is out of bounds, add to set
                if not validate_bounds_of_board(point):
                    out_of_bounds_points.add(point)

            # Remove all out_of_bounds_points from possible bridges
            possible_bridges = possible_bridges.difference(
                out_of_bounds_points)

            # If intersecting points exist, add them to the set of overlapping points
            if len(possible_bridges) > 0:
                overlaps.update(possible_bridges)

    return overlaps


def find_closest_white_piece(group, board):
    """
    Finds the closest white piece to a group, and make it the primary.
    :param group: the group you are currently trying to blow up.
    :param board: the current game state board
    :return: the closest piece to the group, with it's primary flag attribute set to True.
    """
    white_pieces = board.get_white_pieces()

    # Initialise the minimum value to infinity, we aim to improve this
    closest_piece = None
    min_value = math.inf

    for black_stack in group:
        # Get the co-ordinates of the black stack
        black_stack_position = black_stack[1], black_stack[2]

        # Iterate through each stack of white pieces
        for stack_position in white_pieces.keys():

            # Calculate the manhattan distance
            manhattan_value = manhattan_distance(
                stack_position, black_stack_position)

            # If the calculated manhattan distance is less than the current minimum, replace it.
            if manhattan_value < min_value:
                min_value = manhattan_value
                closest_piece = white_pieces[stack_position]

    # Make the closest piece the primary one
    closest_piece.make_primary()

    return closest_piece


def search_surroundings(piece, visited, black_pieces, group, board):
    """
    Searches the surroundings of a piece for adjacent pieces and groups them up
    :param piece: a list containing the stack count and position of a piece
    :param visited :contains a list of pieces that have been operated on
    :param black_pieces: a list of black piece coordinates and stack counts
    :param group:
    :param board: the current board
    :return: idk
    """
    visited.append(piece)
    group.append(piece)
    for move in SEARCH_MOVES:

        # iterates through the surroundings of a chess piece
        if validate_move_bounds((piece[1], piece[2]), move):

            marker = add_vectors((piece[1], piece[2]), move)

            # if a piece is found, next_piece will be assigned the information about the piece,
            # otherwise next_piece is false
            next_piece = detect_piece(marker, visited, black_pieces)

            if next_piece != False:
                search_surroundings(next_piece, visited,
                                    black_pieces, group, board)


# NOTE: This algorithm can definitely be improved with the use of dictionaries to index chess piece locations
# will revamp if necessary
def detect_piece(position, visited, black_pieces):
    """
    Detects if a piece is in a space next to the piece being investigated
    :param position: a tuple containing the x and y co-ordinates of the space to be investigated
    :param visited :contains a list of pieces that have been operated on
    :param black_pieces: a list of black piece coordinates and stack counts 
    :return: a boolean value indicating that there is no piece in the space being investigated\
     or the stack count and co-oridinates of a piece if it is found
    """
    # x and y co-ordinates of position to be investigated
    x = position[0]
    y = position[1]

    # if position has been visited, false is returned
    for piece in visited:
        if x == piece[1] and y == piece[2]:
            return False

    # checks if a piece exists in the investigated position
    for piece in black_pieces:
        if x == piece[1] and y == piece[2]:
            return piece

    return False


# Deprecated
def check_goal(board):
    """
    Check if the goal state for the board has been reached.
    :param board: the current board
    :return: a boolean value indicating when all board flags are set to true.
    """
    # sets all goal flags to false
    check_groups(board)

    # Get the group flags for the board
    record = board.get_group_flag()

    # if a flag is False, return everything as False
    for flag in record:
        if not flag:
            return False
    return True


# Deprecated
def check_groups(board):
    """
    Check all groups on the board and if they have a white piece next to them.
    :param board: the current board
    :return: no explicit return, triggers side effects. sets group flag values to true if near a white piece.
    """
    # sets all group flags to false
    for i in range(0, len(board.group_flag)):
        board.group_flag[i] = False

    # iterates through the surroundings of black groups to detect white pieces and switch on flags
    for key in board.black_dict.keys():
        for move in SEARCH_MOVES:
            if validate_move_bounds((key[0], key[1]), move):
                step = add_vectors(key, move)
                if step in board.white_dict.keys():
                    board.group_flag[board.dict[key].group] = True


# Deprecated
def calculate_group_centres(group_set):
    """
    Given a list of groups, calculate the average co-ordinate for the group,
    effectively finding the centre of the group.
    :param group_set: a list of lists, where each internal list contains all pieces in close proximity to each other.
    :return: a group_set with an added dimension which represents the average co-ordinate (center) of the group.
    """
    group_centres = []
    for group in group_set:
        group_length = len(group)
        x = 0
        y = 0
        for piece in group:
            x += piece[1]
            y += piece[2]

        x_mean_floored, y_mean_floored = math.floor(
            x/group_length), math.floor(y/group_length)
        group_centres.append((x_mean_floored, y_mean_floored))

    return [(group, centre) for group, centre in zip(group_set, group_centres)]
