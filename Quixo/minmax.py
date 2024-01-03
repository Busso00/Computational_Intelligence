from copy import deepcopy
import numpy as np
from game import Move


BORDER_TILES = np.array(
    [[True, True, True, True, True],
    [True, False, False, False, True],
    [True, False, False, False, True],
    [True, False, False, False, True],
    [True, True, True, True, True]])

def possible_moves(board: np.array, player): #NOTE: return only valid moves
    valid_moves = []
    free_tiles = board == 0
    my_tiles = board == player

    valid_tiles = (free_tiles | my_tiles) & BORDER_TILES
    
    for i in range(5):
        for j in range(5):
            if valid_tiles[i][j]:
                for k in range(4):
                    if not ((i == 0 and k==0) or (i==4 and k==1) or (j == 0 and k==2) or (j == 4 and k==3)):
                        valid_moves.append((i,j,Move(k)))

    return valid_moves


def make_ply(board, ply, player): #NOTE: efficient way to make a valid move (must be valid)
    new_board = deepcopy(board)
    
    if ply[2] == Move.TOP:
        new_board [1:ply[0]+1,ply[1]] = new_board[0:ply[0],ply[1]]
        new_board[0,ply[1]] = player
    elif ply[2] == Move.BOTTOM:
        new_board [ply[0]:4,ply[1]] = new_board[ply[0]+1:5,ply[1]]
        new_board[4,ply[1]] = player
    elif ply[2] == Move.LEFT:
        new_board[ply[0],1:ply[1]+1] = new_board[ply[0],0:ply[1]]
        new_board[ply[0],0] = player
    else:
        new_board [ply[0],ply[1]:4] = new_board[ply[0],ply[1]+1:5]
        new_board[ply[0],4] = player

    return new_board


def check_winner(board, player) -> int: #NOTE: not used but applied in practice by the score returned by minmax leaf
    '''Check the winner. Returns the player ID of the winner if any, otherwise returns -1'''
    #reading paper "Quixo is solved emerge from rules that corner case in which player moving his piece create another line of opponents symbol lose"
    #however is really rare evenience

    i_win = False 
    for x in range(board.shape[0]):
        if board[x, 0] != 0:
            if all(board[x, :] == board[x, 0]):
                if player != board[x, 0]:
                    return -player #if last move make complete a row/col of oppo i lose (-player wins)
                i_win = True #check if last move lead me to win 
                
    for y in range(board.shape[1]):
        if board[0, y] != 0:
            if all(board[:, y] == board[0, y]):
                if player != board[0, y]:
                    return -player
                i_win = True
        
    if board[0, 0] != 0:    
        if all([board[x, x] for x in range(board.shape[0])] == board[0, 0]):
            if player != board[0, 0]:
                return -player
            i_win = True

    if board[0, -1] != 0:
        if all([board[x, -1-x] for x in range(board.shape[0])] == board[0, -1]):
            if player != board[0, -1]:
                return -player
            i_win = True
    
    if i_win:
        return player
    
    return 0 #no winner
                

MAX_INT = 10000  

POS_SCORES = np.array([
    [3,2,2,2,3],
    [2,3,2,3,2],
    [2,2,4,2,2],
    [2,3,2,3,2],
    [3,2,2,2,3]
])

TOT_SCORES = np.sum(POS_SCORES)

def heuristic_score(board:np.array, player:int, count: (int, int)): #must be efficient
    
    score = 0
   

    #heuristic1
    #board - player set to 0 positon taken by player, count_nonzero counts opponents or not taken position: 
    #assumption: the higher they are the less probably the player can win -> score is -count
    #in this sense player is trying to prevent opponent to "lock" his moves into keep choosing already taken pieces #NOTE: in testing obtained speedup also
    #score -= np.count_nonzero(board - player) / 25 #max=25
    #heuristic2
    #board + player set to 0 positon taken by opponent, count_nonzero counts player or not taken position: 
    #assumption: the higher they are the more probably the player can win -> score is +count (remember that this scoring happens without appending -val)
    #in this sense player is trying to "lock" opponent into moves that keep choosing already taken pieces #NOTE: can slow down since leave more freedom to player -> more branches
    #score += np.count_nonzero(board + player) / 25 #max=25
    #heuristic3 count of row/col/diag of 4
    
    score += (count[0]-count[1]) / 5 #in case of 4 in a row opponent has higher chance of winning: his move and your move

    score += (count[2]-count[3]) / 25
    #heuristic 4 center
    #score += board[2][2] * player / 25
    #heuristic 5 weight possibilities of quixo (use without h1 and h2)
    score += np.sum(board*POS_SCORES*player) / TOT_SCORES
    
    return score


def eval_terminal_3_4(board, player):
    count_p_4 = 0 #count >4 for player
    count_o_4 = 0 #count >4 for opponent
    count_p_3 = 0 #count >3 for player
    count_o_3 = 0 #count >3 for opponent

    oppo_win = False
    for x in range(board.shape[0]):
        n_p = np.count_nonzero(board[x, :] == player)
        if n_p >= 3:
            if n_p >= 4:
                if n_p == 5:
                    return (MAX_INT,None) # last move created a winning position for opponent (current player) -> lose
                count_p_4 += 1
            count_p_3 += 1
        else:
            n_o = np.count_nonzero(board[x, :] == -player)
            if n_o >= 3:
                if n_o >= 4:
                    if n_o == 5:
                        oppo_win = True # last move make me win (current player lose) -> but i can still win if a following row is mine
                    count_o_4 += 1
                count_o_3 += 1

    if oppo_win:
        return (-MAX_INT, None) # a complete row cannot let opponent complete column or diagonal -> return

    for y in range(board.shape[1]):
        n_p = np.count_nonzero(board[:, y] == player)
        if n_p >= 3:
            if n_p >= 4:
                if n_p == 5:
                    return (MAX_INT,None)
                count_p_4 += 1
            count_p_3 += 1
        elif not oppo_win:
            n_o = np.count_nonzero(board[:, y] == -player)
            if n_o >= 3:
                if n_o >= 4:
                    if n_o == 5:
                        oppo_win = True
                    count_o_4 += 1
                count_o_3 += 1

    if oppo_win:
        return (-MAX_INT, None) # a complete column cannot let opponent complete diagonal -> return 
    
    diag1 = np.diag(board)
    
    n_p = np.count_nonzero(diag1 == player)
    if n_p >= 3:
        if n_p >= 4:
            if n_p == 5:
                return (MAX_INT,None)
            count_p_4 += 1
        count_p_3 += 1
    elif not oppo_win:
        n_o = np.count_nonzero(diag1 == -player)
        if n_o >= 3:
            if n_o >= 4:
                if n_o == 5:
                    return (-MAX_INT, None) #a complete diagonal cannot allow me to have other row/col complete -> return 
                count_o_4 += 1
            count_o_3 += 1
     
    diag2 = np.diag(np.rot90(board))
    
    n_p = np.count_nonzero(diag2 == player)
    if n_p >= 3:
        if n_p >= 4:
            if n_p == 5:
                return (MAX_INT,None)
            count_p_4 += 1
        count_p_3 += 1
    elif not oppo_win:
        n_o = np.count_nonzero(diag2 == -player)
        if n_o >= 3:
            if n_o >= 4:
                if n_o == 5:
                    return (-MAX_INT, None) #a complete diagonal cannot allow me to have other row/col complete -> return 
                count_o_4 += 1
            count_o_3 += 1

    return (0,(count_p_4, count_o_4, count_p_3, count_o_3))


print("heuristic scoring:")
print(f"min: {-MAX_INT}, max: {MAX_INT}")
print(f"positional scores:")
print(POS_SCORES)
print("count aligned: 3/25, 4/5")


def canonical_repr_16simm(board, player): #NOTE: more compact representation like described in "Quixo is Solved" paper are feasible but more expensive (in term of CPU time)

    new_board = deepcopy(board)
    equiv_board_bytes = [(bytes(new_board),player), (bytes(np.flipud(new_board)),player), (bytes(-new_board),-player), (bytes(np.flipud(-new_board)),-player)]
   
    for _ in range(3):
        new_board = np.rot90(new_board)
        equiv_board_bytes += [(bytes(new_board),player), (bytes(np.flipud(new_board)),player), (bytes(-new_board),-player), (bytes(np.flipud(-new_board)),-player)]
    
    return min(equiv_board_bytes, key= lambda x: x[0])



#iterative deepening 
MIN_DEPTH = 1 #approx 40 ply evaluated
MAX_DEPTH = 3 #approx 40*40*40 ply/re-ply/ply evaluated
THRESHOLD = [MAX_INT,0.3,-MAX_INT] #MAX_INT = pick only wis, -MAX_INT = pick all (first player is always max player)
MAX_SIZE = 83886160 # can set a max size for cache to avoid memory error, if not set usually reached in 50000 games
state_cache = {}

#turn are swapped when recurring. max_turn/mul_leaf are pre-computation of f(max_depth): less expensive to have larger stack than calculating every time from max_depth
def alfabeta(board: np.array, player: int, depth: int, alfa: int, beta: int, max_turn: int, mul_leaf: int) -> ((int, int, Move), int, bool): #out of object -> faster call

    val, count = eval_terminal_3_4(board, player)
    if val !=0:
        #max d 3 mul leaf = -1 
        #ret at 2: 3 is max receive - val
        #ret at 1: 2 is min receive + val
        #ret at 0: 1 is max receive - val
        #max d 2 mul leaf = 1
        #ret at 1: 2 is max receive - val 
        #ret at 0: 1 is min receive + val
        #max d 1 mul leaf = -1
        #ret at 0: 1 is max receive - val
        return None, mul_leaf * val * (1 - (depth % 2) * 2) , False 
    
    if depth == 0:
        hs = heuristic_score(board, player, count)
        #max d 3 mul leaf = -1 
        #ret at 0: 1 is max receive - hs
        #max d 2 mul leaf = 1
        #ret at 0: 1 is min receive + hs
        #max d 1 mul leaf = -1
        #ret at 0: 1 is max receive - hs
        return None, mul_leaf * hs, False # - hs because hs is evaluation for current node
    
    possible = possible_moves(board, player)
    if len(possible)==0:
        return None, 0, False
    
    is_max = depth%2 == max_turn

    evaluations = []

    for ply in possible:
        new_board = make_ply(board, ply, player)
        board_turn_key = canonical_repr_16simm(new_board, player)
        
        hit = False
        for d in range(MAX_DEPTH, depth-1, -1):
            if state_cache.get((board_turn_key[0], board_turn_key[1], d, is_max)) and not hit:
                val = state_cache[(board_turn_key[0], board_turn_key[1], d, is_max)]
                hit = True
            elif state_cache.get((board_turn_key[0], board_turn_key[1], d, is_max)):
                del state_cache[(board_turn_key[0], board_turn_key[1], d, is_max)] #remove less precise estimation of value for a move
        
        if not hit:
            _, val, pruned = alfabeta(new_board, -player , depth-1, alfa, beta, max_turn, mul_leaf)
            if not pruned: #if next layer has evaluated all the nodes the value returned is the correct one
                state_cache[(board_turn_key[0], board_turn_key[1], depth, is_max)] = val #particularly useful to store openings
            
        if is_max:
            alfa = max(alfa, val)
        else:
            beta = min(beta, val)
        
        evaluations.append((ply, val))

        if beta <= alfa:
            break
    
    if is_max:
        best = max(evaluations, key=lambda k: k[1])
    else:
        best = min(evaluations, key=lambda k: k[1])
        
    return best[0], best[1], len(evaluations) != len(possible) #if all states are evaluated -> reliable estimate of val


def alfabeta_iter_deep(board, player, min_depth, max_depth): #iterative deepening wrapper

    assert max_depth == MAX_DEPTH and min_depth == MIN_DEPTH, "min_depth must be MIN_DEPTH and max_depth must be MAX_DEPTH"
    t = 0
    for d in range(min_depth, max_depth+1):

        ply, val, _ = alfabeta(board, player, d, -MAX_INT, MAX_INT, d%2, 1 - (d % 2)*2)
        if val >= THRESHOLD[t]:
            return ply, val , d
        t += 1

    assert False, "return val must exist (last threshold must be -MAX_INT)"
