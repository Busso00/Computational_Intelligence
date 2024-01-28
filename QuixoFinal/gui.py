from game import Game, Move, Player
import numpy as np

from copy import deepcopy

import tkinter as tk
from tkinter import messagebox

from minmax import *

import time

#same of calss MyPlayer in main
class MyPlayer(Player):
    def __init__(self, min_depth: int, max_depth: int, tV: [int]) -> None: # min_depth = 1, max_depth = 3 , state_cache = {}, max_int = 10_000, are already included in minmax.py
        super().__init__()
        self.policy = "minmax with alphabeta,iterative deepening,transposition tables"
        self.win = 0
        self._min_depth = min_depth
        self._max_depth = max_depth
        self._tV = tV

    def make_move(self, game: 'Game') -> tuple[tuple[int, int], Move]:


        #mapping board to minmax representation
        board = deepcopy(game._board)
        board = board*2 - 1
        board = np.where(board < -1, 0, board)

        ply, _, _ = alfabeta_iter_deep(board, game.get_current_player() * 2 - 1 , self._min_depth, self._max_depth, self._tV)


        return (ply[1], ply[0]), ply[2] #inverted row col

class GUI(object):

    def __init__(self):
        
        self.root = tk.Tk()
        self.root.title("Quixo Game")
        #input "form"
        self.label = tk.Label(self.root, text="enter a player: for X(first) or O(second)")
        self.entry = tk.Entry(self.root, width=30)
        self.enter = tk.Button(self.root, text="Get Input", command=self.get_input) #NOTE:only command possible: press enter to read value in self.entry
        #padding
        self.entry.pack(pady=10)
        self.enter.pack(pady=10)
        self.label.pack(pady=20)

        #start loop
        self.root.mainloop()
        
    #popup alerts
    def show_alert_invalid_move(self):
        messagebox.showinfo("Information", "invalid move: retry")

    def show_alert_invalid_player(self):
        messagebox.showinfo("Information", "invalid player: enter a player: for X(first) or O(second)")

    #on press of "Get Input" button
    def get_input(self):
        human_turn = self.entry.get()
        if human_turn not in ['X','O']:
            self.show_alert_invalid_player()
            return #do nothing
        
        #instantiate game
        g = GameForHuman(debug = True, gui = self) 
        #define player on basis of user input
        if human_turn == 'X':
            player1 = Human()
            player2 = MyPlayer(1,3,[MAX_INT,0.3,-MAX_INT])
        else:
            player1 = MyPlayer(1,3,[MAX_INT,0.3,-MAX_INT])
            player2 = Human()
        #start playing
        g.play_human(player1, player2) # player selected, game can start 
        
    # destroy each widget individually
    def remove_all_widgets(self):
        for widget in self.root.winfo_children():
            widget.destroy()

    #set key value and update _key_pressed wait-variable
    def on_key(self, event):  
        if event.keysym == 'Up':
            self._key_value = Move.TOP
        elif event.keysym == 'Down':
            self._key_value = Move.BOTTOM
        elif event.keysym == 'Left':
            self._key_value = Move.LEFT
        elif event.keysym == 'Right':
            self._key_value = Move.RIGHT
        elif event.keysym == 'Escape':
            exit()

        self._key_pressed.set(value = True)

    #only for visualization (not interactive)
    def update_gui(self, game: 'Game', winner: int):

        self.remove_all_widgets()    

        if winner == -1:
            self.label = tk.Label(self.root, text="Opponent is thinking")
        elif winner == 0:
            self.label = tk.Label(self.root, text="Quixo! X win")
        else:
            self.label = tk.Label(self.root, text="Quixo! O win")
        self.label.pack(side=tk.TOP, pady=20)
        
        #button to visualize state of grid
        self.frame = tk.Frame(self.root)
        self.frame.pack(side=tk.BOTTOM)
        self.buttons = [[None]*5 for _ in range(5)]
        for i in range(5):
            for j in range(5):
                if game._board[i][j] == 0:
                    value = 'X'
                elif game._board[i][j] == 1:
                    value = 'O'
                else:
                    value = ' '
                button = tk.Button(self.frame, text=value, width=10, height=5) #button cannot be pressed (only for visualization)
                button.grid(row=i, column=j)
                self.buttons[i][j] = button
        
        self.root.update()

    #interactive gui (press button on board to select move)
    def update_gui_with_player(self, human_player: Player, game: 'Game'):

        self.remove_all_widgets()        

        self.label = tk.Label(self.root, text="Click on an position to select it and move it with keyboard arrows")
        self.label.pack(side=tk.TOP, pady=20)
        
        #button to visualize state of grid and allow selection of move
        self.frame = tk.Frame(self.root)
        self.frame.pack(side=tk.BOTTOM)
        self.buttons = [[None]*5 for _ in range(5)]
        for i in range(5):
            for j in range(5):
                if game._board[i][j] == 0:
                    value = 'X'
                elif game._board[i][j] == 1:
                    value = 'O'
                else:
                    value = ' '
                #button have effect when clicked
                button = tk.Button(self.frame, text=value, width=10, height=5, command=lambda row=i, col=j: human_player.make_move(self, row, col)) 
                button.grid(row=i, column=j)
                self.buttons[i][j] = button
        
        #use state variable to control "return values" of actions
        self._button_pressed = tk.BooleanVar(value = False)
        self._move_value = ((None, None), None)

        #key have effect when pressed
        self.root.bind("<Up>", self.on_key)
        self.root.bind("<Down>", self.on_key)
        self.root.bind("<Left>", self.on_key)
        self.root.bind("<Right>", self.on_key)
        self.root.bind("<Escape>", self.on_key)
        self._key_pressed = tk.BooleanVar(value=False)
        self._key_value = None
        self.root.focus_set()

        self.root.update()



class Human(Player):
    def __init__(self) -> None:
        super().__init__()
        self.policy = "human"
    
    def make_move(self, gui:GUI, row: int, col: int ) -> tuple[tuple[int, int], Move]:
        
        #reset key (direction) values
        gui._key_pressed.set(False) 
        gui._key_value = None       

        #make button look pressed
        gui.buttons[row][col].config(relief=tk.SUNKEN, state = "disabled")
        gui.label.config(text="Press an arrow. To cancel the selection of a tile make an invalid move")

        while not gui._key_pressed.get():
            gui.root.wait_variable(gui._key_pressed)#wait until key is pressed
        #make button look released
        gui.buttons[row][col].config(relief=tk.RAISED, state = "normal") #re-enable button

        shift = gui._key_value #caprure value pressed (move)

        gui._return_value = ((col, row), shift)

        gui._button_pressed.set(True)



class GameForHuman(Game):
        
    def __init__(self, debug = False, gui = None) -> None:
        super().__init__()
        self._debug = debug
        self._gui = gui


    def play_human(self, player1: Player, player2: Player) -> int:
        '''Play the game. Returns the winning player'''

        players = [player1, player2]
        self.current_player_idx = 1
        winner = -1
       
        while winner == -1:
            self.current_player_idx += 1 #swap strategies
            self.current_player_idx %= len(players)
           
            ok = False
            while not ok:
                
                if players[self.current_player_idx].policy != "human":
                    #pause game response to help human check if move was valid
                    time.sleep(2) 
                    from_pos, slide = players[self.current_player_idx].make_move(self)

                else:
                    self._gui.update_gui_with_player(players[self.current_player_idx], self) # update gui making it clickable
                    
                    while not self._gui._button_pressed.get():
                        self._gui.root.wait_variable(self._gui._button_pressed)

                    self._gui._button_pressed.set(False)

                    from_pos, slide = self._gui._return_value
                
                ok = super()._Game__move(from_pos, slide, self.current_player_idx)#workaround to not change class Game
                #https://stackoverflow.com/questions/47019802/inheriting-class-attribute-with-double-underscore
                
                if players[self.current_player_idx].policy != "human": #ai players already do only possible moves
                    assert ok, f"BOT PLAYER CANNOT MAKE INVALID MOVES:\n on board:\n {self._board}\n invalid move: {from_pos, slide} by player: {self.current_player_idx}"
                else:
                    if not ok:
                        self._gui.show_alert_invalid_move()

            
            winner = self.check_winner()

            self._gui.update_gui(self, winner) #after every move update gui visualization


        return winner
