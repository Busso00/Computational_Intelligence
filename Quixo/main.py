import random
from game import Game, Move, Player
from minmax import *
from gui import GUI

import tqdm
from tqdm import tqdm

import sys
    
DEBUG = True

class RandomPlayer(Player):
    def __init__(self) -> None:
        super().__init__()
        self.policy = "random"
        self.win = 0

    def make_move(self, game: 'Game') -> tuple[tuple[int, int], Move]:
        if DEBUG:
            print(game._board)
        #mapping board to minmax representation
        board = deepcopy(game._board)
        board = board*2 - 1
        board = np.where(board < -1, 0, board)

        ply = random.choice(possible_moves(board, game.get_current_player() * 2 - 1))
        if DEBUG:
            print(ply)
        return (ply[1], ply[0]), ply[2] #inverted row col

class MyPlayer(Player):
    def __init__(self) -> None: # min_depth = 1, max_depth = 3 , state_cache = {}, max_int = 10_000, are already included in minmax.py
        super().__init__()
        self.policy = "minmax with alphabeta,iterative deepening,transposition tables"
        self.win = 0

    def make_move(self, game: 'Game') -> tuple[tuple[int, int], Move]:
        if DEBUG:
            print(game._board)
        #mapping board to minmax representation
        board = deepcopy(game._board)
        board = board*2 - 1
        board = np.where(board < -1, 0, board)

        ply, _, _ = alfabeta_iter_deep(board, game.get_current_player() * 2 - 1 , 1, 3)
        if DEBUG:
            print(ply)
        return (ply[1], ply[0]), ply[2] #inverted row col

N_GAMES = 25000 

if __name__ == '__main__':
    g = Game()
    g.print()
    player1 = MyPlayer()
    player2 = RandomPlayer()
    winner = g.play(player1, player2)
    g.print()
    print(f"Winner: Player {winner}")

    gui = GUI() #start a GUI to play quixo against minmax agent

    win = 0
    lose = 0
    print(f"test alfabeta: {N_GAMES} matches")
    custom_bar_format = "{l_bar}{bar:50}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}]"
    progress_bar = tqdm(range(N_GAMES),dynamic_ncols=True,desc="Game",colour="green",total=N_GAMES,mininterval=0.5,bar_format=custom_bar_format,ncols=100)

    for game in progress_bar:

        if game == 10:
            DEBUG = False

        g = Game()
        random.seed(game)
        if game%2 == 0:
            player1 = MyPlayer()
            player2 = RandomPlayer()
        else:
            player2 = MyPlayer()
            player1 = RandomPlayer()

        winner = g.play(player1, player2)

        if DEBUG:
            print(g._board)
            print(f"winner: {winner}, agent: {game%2}")

        if winner == game % 2:
            win += 1
        else:
            lose += 1

        if game % 2500 == 0:
            print(f"lose @{game}: {lose}")
        
        progress_bar.set_description(f"won: {win}, lost: {lose}, size dict: {sys.getsizeof(state_cache)} bytes") #monitoring slowdown: in 300 game around 1M entries
