import numpy as np
import random
from albanianRodentDinner.entities import *

# Initializes the table 
def init_table(table):
	for i in range (0,8):
		for j in range (0,8): 
			for k in range (0,32):  
				table[i][j][k] = random.randint(0, 1000000000) 


# Computes the hash value of a given board 
def compute_hash(board, table):
	hash_val = 0
	for i in range (0,8):
		for j in range (0,8): 
			

			if (i,j) in board.dict.keys():
				piece = index_of(board,board.dict[(i,j)])
				'''
				print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
				print((i,j))
				print("piece = "+ str(piece))
				print(table[i][j][piece])
				print(type(int(table[i][j][piece])))
				print("hash = "+ str(hash_val))
				print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
				'''
				hash_val =  np.bitwise_xor(int(table[i][j][piece]),hash_val)
	return hash_val


def index_of(board,piece):	
	if piece.team == WHITE:
		return int(piece.count - 1)
	else:
		return int(piece.count + 15)

def compute_move_hash(board, hash_val, hash_table, current_position, future_position, pre_del, post_del, pre_add, post_add):
	#print("++++++++++++++++++++++")
	#print(hash_val)
	if pre_add !=  None:
		hash_val = np.bitwise_xor(int(hash_table[current_position[0]][current_position[1]][pre_add.count]),hash_val)
	#print(hash_val)
	hash_val = np.bitwise_xor(int(hash_table[current_position[0]][current_position[1]][pre_del.count]),hash_val)
	#print(hash_val)
	hash_val = np.bitwise_xor(int(hash_table[future_position[0]][future_position[1]][post_add.count]),hash_val)
	#print(hash_val)
	if post_del !=  None:
		hash_val = np.bitwise_xor(int(hash_table[future_position[0]][future_position[1]][post_del.count]),hash_val)
	#print(hash_val)
	#print("++++++++++++++++++++++")
	return hash_val

def compute_boom_hash(board, hash_val, hash_table, exploded):


	for i in exploded:
		#print("PRE",hash_val)
		hash_val = np.bitwise_xor(int(hash_table[i[0]][i[1]][exploded[i].count]),hash_val)
		#print("POST",hash_val)
	return hash_val