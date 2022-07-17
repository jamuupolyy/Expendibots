import copy
# Functions to define game structure

# Constants to define movements
BLACK = 0
WHITE = 1

inverse_color = {WHITE: BLACK, BLACK: WHITE}

LEFT = (-1, 0)
RIGHT = (1, 0)
UP = (0, 1)
DOWN = (0, -1)
UPPER_LEFT = (-1, 1)
UPPER_RIGHT = (1, 1)
LOWER_LEFT = (-1, -1)
LOWER_RIGHT = (1, -1)

# contains the inverses of moves
inverse_move = {UP: DOWN, RIGHT: LEFT, DOWN: UP, LEFT: RIGHT, None: None}

# Define all possible agent moves
MOVES = [UP, RIGHT, DOWN, LEFT]

# Define the search area
SEARCH_MOVES = [UP, UPPER_RIGHT, RIGHT, LOWER_RIGHT,
                DOWN, LOWER_LEFT, LEFT, UPPER_LEFT]

# Define bounds of the board
BOARD_LOWER_BOUND = 0
BOARD_UPPER_BOUND = 7


def simulate_move(current_position, move, n, board, max_moves, spaces, color):
    pre_add = None
    post_add = None
    pre_del = None
    post_del = None


    if is_legal_move(current_position, scale_vector(move, spaces), board, color):
        future_position = add_vectors(current_position, scale_vector(move, spaces))
        
        pre_del = (board.dict[current_position])
        if future_position in board.dict.keys():

            post_del = (board.dict[future_position])
        #board.print()
        #print(pre_del, post_del,"$$$$", pre_add, post_add)
        if color == WHITE:
            board.move_white_piece(current_position, future_position, n, (max_moves - n))
        else:
            board.move_black_piece(current_position, future_position, n, (max_moves - n))

        if current_position in board.dict.keys():

            pre_add = (board.dict[current_position])
        post_add = (board.dict[future_position])
        #board.print()
        #print(current_position,future_position)
        #print(pre_del, post_del,"----", pre_add, post_add)


        return (current_position, future_position, pre_del, post_del, pre_add, post_add)

    # Return False if piece cannot be moved
    return False


def all_possible_board_positions():
    """
    Get the set of all board co-ordinates.
    :return: set of all board co-ordinates.
    """
    all_positions = set()

    for x in range(BOARD_LOWER_BOUND, BOARD_UPPER_BOUND+1):
        for y in range(BOARD_LOWER_BOUND, BOARD_UPPER_BOUND+1):
            position = (x, y)
            all_positions.add(position)

    return all_positions


def add_vectors(v1, v2):
    """
    Function to add two 2D vectors together.
    A vector is a tuple of two numbers.
    :param v1: a vector
    :param v2: a vector
    :return: vector that has been added together
    """
    return v1[0] + v2[0], v1[1] + v2[1]


def scale_vector(v, scalar):
    """
    Scale and return a given vector.
    :param v: a vector, represented by a 2D tuple
    :param scalar: any scalar value (we work with integers in Expendibots)
    :return: scaled vector
    """
    return v[0] * scalar, v[1] * scalar


def is_legal_move(current_position, possible_move, board, colour):
    """
    Determine if a move is legal or not.
    A legal move is one which does not violate the bounds of the board, nor does it step onto opponents pieces.
    :param current_position: a tuple representing co-ordinates
    :param possible_move: one of the 4 possible moves
    :param board: the current board
    :return: a boolean value indicating if a move is legal.
    """

    if colour == WHITE:
        inverse_dict = board.black_dict
    else:
        inverse_dict = board.white_dict

    # Check if new move conflicts with boundaries of the board
    if not validate_move_bounds(current_position, possible_move):
        return False

    # Check if new move conflicts with other pieces on the board.
    if add_vectors(current_position, possible_move) in inverse_dict.keys():
        return False
    return True


def move_piece(current_position, move, n, board, max_moves, spaces, colour):
    """
    Move a given piece, represented by co-ordinates. If a move is not possible, return False.
    :param colour:
    :param current_position: co-ordinates for a piece, represented as a tuple where positions 0 and 1 are x and y respectively.
    :param move: one of the 4 possible moves (LEFT, RIGHT, UP, DOWN)
    :param n: the amount of pieces to move.
    :param max_moves the maximum piece count of the stack. this determines how far a piece can move.
    :param board: the current board
    :param board: number of spaces to move
    :return: the new co-ordinates of the given piece if the move is possible, otherwise return False.
    """
    if is_legal_move(current_position, scale_vector(move, spaces), board, colour):
        future_position = add_vectors(
            current_position, scale_vector(move, spaces))
        if colour:
            board.move_white_piece(current_position, future_position, n, (max_moves - n))
        else:
            board.move_black_piece(current_position, future_position, n, (max_moves - n))

        return future_position

    # Return False if piece cannot be moved
    return False


def validate_move_bounds(current_position, possible_move):
    """
    Determine if a move violates the bounds of the board.
    :param current_position: a tuple representing co-ordinates, where position[0], position[1] are the x,y co-ordinates
    :param possible_move: one of the 4 possible moves
    :return: a boolean value indicating if a move is within bounds.
    """
    if not validate_bounds_of_board(add_vectors(current_position, possible_move)):
        return False
    return True


def validate_bounds_of_board(position):
    """
    Determine if a co-ordinate is outside the bounds of the board.
    :param position: a tuple representing co-ordinates, where position[0], position[1] are the x,y co-ordinates
    :return: a boolean value indicating if a position is within bounds.
    """
    if position[0] < BOARD_LOWER_BOUND or \
            position[1] < BOARD_LOWER_BOUND or \
            position[0] > BOARD_UPPER_BOUND or \
            position[1] > BOARD_UPPER_BOUND:
        return False

    return True
