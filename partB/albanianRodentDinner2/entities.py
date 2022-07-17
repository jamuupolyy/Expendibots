from albanianRodentDinner.util import *
from albanianRodentDinner.moves import *

# Constants
BLACK = 0
WHITE = 1


class Piece:
    def __init__(self, count, team, group):
        self.count = count
        self.team = team
        self.group = group
        self.primary = False

    def make_primary(self):
        self.primary = True

    def remove_primary(self):
        self.primary = False

    def get_count(self):
        return self.count

    def get_team(self):
        return self.team

    def get_group(self):
        return self.group

    def get_primary_status(self):
        return self.primary


class Board:
    def __init__(self):
        self.f = 0
        self.g = 0
        self.white_dict = {}
        self.black_dict = {}
        self.dict = {}
        self.group_flag = []
        self.black_group_set = None
        self.white_group_set = None

    def remove_groups(self, exploded):
        """
        removes groups that get blown up from groupset
        :param exploded: contain stacks that get blown up
        """
        groups_to_remove = []
        for group in self.black_group_set:
            for stack in group:
                if (stack[1], stack[2]) in exploded:
                    if group not in groups_to_remove:

                        groups_to_remove.append(group)
        for i in groups_to_remove:
            self.black_group_set.remove(i)
            
        white_groups_to_remove = []
        for group in self.white_group_set:
            for stack in group:
                if (stack[1], stack[2]) in exploded:
                    if group not in white_groups_to_remove:

                        white_groups_to_remove.append(group)
        for i in white_groups_to_remove:
            self.white_group_set.remove(i)

    def boom(self, piece):
        """
        removes blown up pieces from a dictionary
        :param piece: stack that initiaties boom
        """
        explode_dict = {}
        exploded = self.simulate_boom(piece)
        exploded.append(piece)
        self.remove_groups(exploded)

        for i in exploded:
            explode_dict[i] = self.dict[i]
            self.dict.pop(i, None)
            self.white_dict.pop(i, None)
            self.black_dict.pop(i, None)
        
        return explode_dict

    def get_surroundings(self, piece):
        """
        get surrounding pieces of a piece
        :return: list of surrounding pieces
        """
        radius = []
        x = piece[0]
        y = piece[1]
        for move in SEARCH_MOVES:
            if validate_move_bounds((x, y), move):

                marker = add_vectors((x, y), move)

                if marker in self.dict.keys():
                    radius.append(marker)
        return radius

    def simulate_boom(self, piece):
        """
        gets all the pieces that will be blown up in a chain explosion, excluding the 
        piece that triggers the explosion
        :param piece: piece that triggers the explosion
        :return: list of pieces that get blown up in a chain explosion except
        """
        visited = []
        unvisited = []
        visited.append(piece)
        unvisited = self.get_surroundings(piece) + unvisited

        while unvisited != []:
            key = unvisited.pop(0)
            visited.append(key)
            surroundings = self.get_surroundings(key)
            for i in surroundings:
                if (i not in visited) and (i not in unvisited):
                    unvisited.append(i)
        visited.remove(piece)
        return visited

    def print(self):
        """
        Print the current board.
        :return: print the board to stdout
        """
        print_template = {}

        temp = []
        for key in self.white_dict:
            temp.append([self.white_dict[key].count, key[0], key[1]])
        print_template['white'] = temp

        alt_temp = []
        for key in self.black_dict:
            alt_temp.append([self.black_dict[key].count, key[0], key[1]])
        print_template['black'] = alt_temp
        print_board(data_to_board_dict(print_template))

    def move_white_piece(self, current_position, future_position, n, remainder):
        """
        moves a piece, given the direction, step and pieces to move
        :param current_position: current position of stack
        :param future_position: co ordinates to move piece to
        :param n: pieces to move from a stack
        :param remainder: pieces left on the old position
        """
        remainder = self.white_dict[current_position].count - n
        future_stack_count = 0

        if future_position in self.white_dict:
            future_stack_count = self.white_dict[future_position].count

        self.white_dict[future_position] = Piece(
            n + future_stack_count, WHITE, -1)
        self.dict[future_position] = Piece(n + future_stack_count, WHITE, -1)
        self.register_primary(future_position)

        self.white_dict.pop(current_position, None)
        self.dict.pop(current_position, None)

        if remainder > 0:
            self.white_dict[current_position] = Piece(remainder, WHITE, -1)
            self.dict[current_position] = Piece(remainder, WHITE, -1)

    def move_black_piece(self, current_position, future_position, n, remainder):
        """
        moves a piece, given the direction, step and pieces to move
        :param current_position: current position of stack
        :param future_position: co ordinates to move piece to
        :param n: pieces to move from a stack
        :param remainder: pieces left on the old position
        """
        remainder = self.black_dict[current_position].count - n
        future_stack_count = 0

        if future_position in self.black_dict:
            future_stack_count = self.black_dict[future_position].count

        self.black_dict[future_position] = Piece(
            n + future_stack_count, BLACK, -1)
        self.dict[future_position] = Piece(n + future_stack_count, BLACK, -1)

        self.black_dict.pop(current_position, None)
        self.dict.pop(current_position, None)

        if remainder > 0:
            self.black_dict[current_position] = Piece(remainder, BLACK, -1)
            self.dict[current_position] = Piece(remainder, BLACK, -1)   

    def register_primary(self, piece):
        """
        registers a primary piece for movement in ida
        :param piece: current position of piece
        """
        self.white_dict[(piece[0], piece[1])].primary = True
        self.dict[(piece[0], piece[1])].primary = True

    def register_black_group_set(self, black_group_set):
        """
        registers a groupset
        :param group_set: 2d list of black groups
        """
        self.black_group_set = black_group_set

    def register_white_group_set(self, white_group_set):
        """
        registers a groupset
        :param group_set: 2d list of black groups
        """
        self.white_group_set = white_group_set

    def register_black_pieces(self, data):
        """
        registers black pieces in dictionaries
        :param data: data about black stacks
        """
        for i in range(0, len(data)):
            for piece in data[i]:
                new_piece = Piece(piece[0], BLACK, i)
                self.black_dict[(piece[1], piece[2])] = new_piece
                self.dict[(piece[1], piece[2])] = new_piece

    def register_white_pieces(self, data):
        """
        registers white pieces in dictionaries
        :param data: data about white stacks
        """
        for i in range(0, len(data)):
            for piece in data[i]:
                new_piece = Piece(piece[0], WHITE, i)
                self.white_dict[(piece[1], piece[2])] = new_piece
                self.dict[(piece[1], piece[2])] = new_piece

    def register_data(self, black_group_set, white_group_set, data):
        """
        registers data in board class
        :param count: number of black groups
        :param group_set: 2d list of black groups
        :param data: input data
        """
        # calculate the centres for each group
        self.register_black_group_set(black_group_set)
        self.register_white_group_set(white_group_set)
        self.register_black_pieces(black_group_set)
        self.register_white_pieces(white_group_set)

    def get_dict(self):
        """
        returns dictionary
        :return: dictionary
        """
        return self.dict

    def get_black_pieces(self):
        """
        Get the black pieces of a board.
        :return: a dictionary containing the black pieces of a board.
        """
        black_pieces = {}
        if len(self.dict) == 0:
            return black_pieces

        else:
            for position in self.dict.keys():
                if self.dict[position].get_team() == BLACK:
                    black_pieces[position] = self.dict[position]
            return black_pieces

    def get_white_pieces(self):
        """
        Get the white pieces of a board.
        :return: a dictionary containing the white pieces of a board.
        """
        white_pieces = {}
        if len(self.dict) == 0:
            return white_pieces

        else:
            for position in self.dict.keys():
                if self.dict[position].get_team() == WHITE:
                    white_pieces[position] = self.dict[position]
            return white_pieces

    def get_white_group_set(self):
        """
        returns group_set
        :return: group_set
        """
        return self.white_group_set

    def get_black_group_set(self):
        """
        returns group_set
        :return: group_set
        """
        return self.black_group_set

    def get_piece_count(self, colour):
        """
        Count number of pieces a team has given a colour.
        :param colour:
        :return: count of number of individual pieces a team has.
        """
        pieces = self.get_white_pieces() if colour else self.get_black_pieces()

        return sum(pieces[piece].get_count() for piece in pieces)
