from copy import deepcopy
import numpy as np
from game import Move #original enum

#all this methods are outside of a class for efficiency reason (lot of test to run)

BORDER_TILES = np.array(
    [[True, True, True, True, True],
    [True, False, False, False, True],
    [True, False, False, False, True],
    [True, False, False, False, True],
    [True, True, True, True, True]])

#efficient way to generate all possible moves (not big impact on time: not called at depth 0)
def possible_moves(board: np.array, player: int) -> [(int, int, Move)]: 
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

#efficient way to make a ply, move must be already validated
def make_ply(board: np.array, ply: (int, int, Move), player: int) -> np.array:

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

MAX_INT = 10000  
#scores are based on number of col/row/diag of which a tile makes part
POS_SCORES = np.array([
    [3,2,2,2,3],
    [2,3,2,3,2],
    [2,2,4,2,2],
    [2,3,2,3,2],
    [3,2,2,2,3]
])
TOT_SCORES = np.sum(POS_SCORES)

def heuristic_score(board:np.array, player:int, count: (int, int)) -> int: #must be efficient
    
    score = 0

    #heuristic 1 and 2: count mine-count opponent -> heuristic 5 is better

    #heuristic3: count of row/col/diag of 4 (later also 3)
    #NOTE: my idea
    score += (count[0]-count[1]) / 5 #in case of 4 in a row opponent has higher chance of winning: his move and your move
    score += (count[2]-count[3]) / 25

    #heuristic 4: center control
    #NOTE: used @ https://github.com/Berkays/Quixo/blob/master/ai.py
    #score += board[2][2] * player / 25
    #heuristic 4 not applied -> heuristic 5 already takes in account for center in a more balanced way

    #heuristic 5: n belongings to line
    #NOTE: my idea
    score += np.sum(board*POS_SCORES*player) / TOT_SCORES
    
    return score


def eval_terminal_3_4(board: np.array, player:int) -> (int, (int, int, int, int) ):
    #count is embedded in terminal evaluations to not call another function that increase the cost
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
                    return (MAX_INT,None) # last move created a winning position for opponent of the player who last moved -> player (arg) win
                count_p_4 += 1
            count_p_3 += 1
        elif not oppo_win:
            n_o = np.count_nonzero(board[x, :] == -player)
            if n_o >= 3:
                if n_o >= 4:
                    if n_o == 5:
                        oppo_win = True # last move created a winning position for the player who last moved -> player (arg) can lose
                    count_o_4 += 1
                count_o_3 += 1

    if oppo_win: # last move end up completing only a row for opponent (who last moved) -> player (arg) lose
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
    else:
        n_o = np.count_nonzero(diag1 == -player)
        if n_o >= 3:
            if n_o >= 4:
                if n_o == 5:
                    return (-MAX_INT, None) #a complete diagonal cannot let opponent complete other diagonal -> return 
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
    else:
        n_o = np.count_nonzero(diag2 == -player)
        if n_o >= 3:
            if n_o >= 4:
                if n_o == 5:
                    return (-MAX_INT, None)
                count_o_4 += 1
            count_o_3 += 1

    return (0,(count_p_4, count_o_4, count_p_3, count_o_3))


print("heuristic scoring:")
print(f"min: {-MAX_INT}, max: {MAX_INT}")
print(f"positional scores:")
print(POS_SCORES)
print("count aligned: 3/25, 4/5")

#NOTE: more compact representation like described in "Quixo is Solved" paper are feasible but more expensive (in term of CPU time)
#NOTE: simmetry explotied as suggested by professor and the paper cited
def canonical_repr_16simm(board: np.array, player: int) -> (np.array, int):

    new_board = deepcopy(board)
    equiv_board_bytes = [(bytes(new_board),player), (bytes(np.flipud(new_board)),player), (bytes(-new_board),-player), (bytes(np.flipud(-new_board)),-player)]
   
    for _ in range(3):
        new_board = np.rot90(new_board)
        equiv_board_bytes += [(bytes(new_board),player), (bytes(np.flipud(new_board)),player), (bytes(-new_board),-player), (bytes(np.flipud(-new_board)),-player)]
    
    return min(equiv_board_bytes, key= lambda x: x[0])


state_cache = {}

#NOTE: alfabeta implementation found @ "Algorithms Explained – minimax and alpha-beta pruning" on youtube, slightly modified
#turn are swapped when recurring. max_turn/mul_leaf are pre-computation of f(max_depth): less expensive to have larger stack than calculating every time from max_depth

#turn are naturally swapped when recurring
def alfabeta(board: np.array, player: int, depth: int, alfa: int, beta: int, max_turn: int, mul_leaf: int , max_depth: int) -> ((int, int, Move), int, bool): #out of object -> faster call

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
    postponed_eval = []
    for ply in possible:
        new_board = make_ply(board, ply, player)
        board_turn_key = canonical_repr_16simm(new_board, player) #1h10min
        
        hit = False
        for d in range(max_depth, depth-1, -1):
            if state_cache.get((board_turn_key[0], board_turn_key[1], d, is_max)) and not hit: 
                val = state_cache[(board_turn_key[0], board_turn_key[1], d, is_max)]
                hit = True
            elif state_cache.get((board_turn_key[0], board_turn_key[1], d, is_max)):
                del state_cache[(board_turn_key[0], board_turn_key[1], d, is_max)]
        
        if not hit:
            if depth > 1:
                postponed_eval.append((ply, new_board, board_turn_key)) #require tree search    
            else: #at depth 1 just 1 level of recursion cost the same -> evaluate directly
                _, val, pruned = alfabeta(new_board, -player , depth-1, alfa, beta, max_turn, mul_leaf, max_depth) 
                if not pruned: #if next layer has evaluated all the nodes the value returned is the correct one
                    state_cache[(board_turn_key[0], board_turn_key[1], depth, is_max)] = val #useful to store openings
                
                if is_max:
                    alfa = max(alfa, val)
                else:# first state that maximizes outcome (my_outcome = -oppo_outcome (win>loss for oppo) in terminal state) is 2
                    beta = min(beta, val)
                

                evaluations.append((ply, val))
                
                if beta <= alfa:
                    break
        else:

            if is_max:
                alfa = max(alfa, val)
            else:# first state that maximizes outcome (my_outcome = -oppo_outcome (win>loss for oppo) in terminal state) is 2
                beta = min(beta, val)    

            evaluations.append((ply, val))

            if beta <= alfa:
                break
    
    if beta <= alfa or depth <= 1:#found an optimal move already cached
        if is_max:
            best = max(evaluations, key=lambda k: k[1])
        else:
            best = min(evaluations, key=lambda k: k[1])
            
        return best[0], best[1], len(evaluations) != len(possible)


    for ply_board_key in postponed_eval:
        _, val, pruned = alfabeta(ply_board_key[1], -player , depth-1, alfa, beta, max_turn, mul_leaf, max_depth)
        if not pruned: #if next layer has evaluated all the nodes the value returned is the correct one
            state_cache[(ply_board_key[2][0], ply_board_key[2][1], depth, is_max)] = val #useful to store openings

        if is_max:
            alfa = max(alfa, val)
        else:# first state that maximizes outcome (my_outcome = -oppo_outcome (win>loss for oppo) in terminal state) is 2
            beta = min(beta, val)
        
        evaluations.append((ply_board_key[0], val))

        if beta <= alfa:
            break

    if is_max:
        best = max(evaluations, key=lambda k: k[1])
    else:
        best = min(evaluations, key=lambda k: k[1])
            
    return best[0], best[1], len(evaluations) != len(possible)


def alfabeta_iter_deep(board, player, min_depth, max_depth, tV):

    t = 0
    for d in range(min_depth, max_depth+1):

        ply, val, _ = alfabeta(board, player, d, -MAX_INT, MAX_INT, d%2, 1 - (d % 2)*2, max_depth)
        if val >= tV[t]:
            return ply, val , d
        t += 1 

    assert False, "return val mus be > -MAX_INT"