import tkinter as tk
import random
import time
from tkinter import messagebox
from tkinter import simpledialog
from pygame import mixer
from threading import Thread
from threading import stack_size


class MyDialog(tk.simpledialog.Dialog):
    def __init__(self, parent, title):
        self.num_of_players = 0
        self.num_real_players = 0
        super().__init__(parent, title)

    def body(self, frame):
        frame.config(bg="#eb2f06")
        frameInstructions = tk.Frame(frame, bg="#eb2f06")
        frameInstructions.grid(row=0, column=0, pady=14)
        self.headingLabel = tk.Label(frameInstructions, text="How to Play?", font=("Times New Roman", 20), fg="white", bg="black", padx=10)
        self.headingLabel.pack(pady=3)
        howtoPlay = "\n- Click on Roll Dice button\nto roll the dice\n- Player gets a bonus dice roll if dice is 6.\n- Goal is to reach the 100th tile.\n- Press [f] key for fullscreen\n- Press [Esc] key to exit fullscreen\n\nPower-ups:\n- Shield (Tile 15): Protects from one snake\n- Double Move (Tile 45): Extra roll\n- Teleport (Tile 75): Move forward randomly"
        wooden_board_Label = tk.Label(frameInstructions, text=howtoPlay, bg="#eb2f06", fg="white", compound=tk.CENTER, font=("Times New Roman", 20))
        wooden_board_Label.pack()

        self.frameName = tk.Frame(frame, bg="#eb2f06")
        self.frameName.grid(row=0, column=1)

        tk.Label(self.frameName, width=30, text="Select number of players", bg="#eb2f06", font=("Comic Sans MS", 17), fg="black").pack(pady=9)
        num_players_string_list = ["Two", "Three", "Four"]
        self.x = tk.IntVar()
        self.choice_frame = tk.Frame(self.frameName)
        self.choice_frame.pack()
        for ptr in range(len(num_players_string_list)):
            radio = tk.Radiobutton(self.choice_frame, value=ptr, text=num_players_string_list[ptr], variable=self.x, font=("Times New Roman", 20), bg="#eb2f06", activebackground="#eb2f06")
            radio.pack(side=tk.LEFT)

        tk.Label(self.frameName, text="Enter number of real (human) players", bg="#eb2f06", font=("Comic Sans MS", 17), fg="black").pack(pady=10)
        self.real_players_entry = tk.Entry(self.frameName, font=("Comic Sans MS", 16))
        self.real_players_entry.pack(pady=5)
        return frame

    def ok_pressed(self):
        self.num_of_players = self.x.get() + 2
        try:
            self.num_real_players = int(self.real_players_entry.get())
            if self.num_real_players > self.num_of_players or self.num_real_players < 1:
                raise ValueError
        except ValueError:
            messagebox.showerror("Invalid Input", "Please enter a valid number of real players (1 to total players)")
            return
        self.destroy()

    def buttonbox(self):
        ok_button = tk.Button(self.frameName, text="Play", command=self.ok_pressed, bg="black", activebackground="brown", font=("Comic Sans MS", 17), fg="white")
        ok_button.pack(pady=10)
        self.bind("<Return>", lambda event: self.ok_pressed())


def mydialog(app):
    dialog = MyDialog(title="Snakes and Ladders - Choose number of players", parent=app)
    SnakesandLadders.num_players = dialog.num_of_players
    SnakesandLadders.num_real_players = dialog.num_real_players


class SnakesandLadders:
    num_players = 0
    num_real_players = 0

    def create_power_up_images(self):
        # Create power-up images on the board
        for tile, power_up in self.power_up_tiles.items():
            if tile in self.tile_coords_map:
                x, y = self.tile_coords_map[tile]
                if power_up == "shield":
                    self.canvas1.create_image(x + 35, y + 35, image=self.shield_image)
                elif power_up == "double_move":
                    self.canvas1.create_image(x + 35, y + 35, image=self.double_move_image)
                elif power_up == "teleport":
                    self.canvas1.create_image(x + 35, y + 35, image=self.teleport_image)

    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Snakes and Ladders")
        self.root.geometry("1300x1000")
        self.root.attributes('-fullscreen', True)
        self.root.config(bg="#BEE9E4")

        self.winner = False
        self.currentPlayer = 0
        self.all_sound_active = True
        self.bonus_active = True

        # Initialize power-up properties first
        self.power_up_tiles = {
            15: "shield",
            45: "double_move",
            75: "teleport"
        }
        self.player_power_ups = [[] for _ in range(4)]

        mydialog(self.root)

        self.players = list(range(self.num_players))
        self.activePlayers = [False] * self.num_players
        self.player_tile_positions = [0] * self.num_players
        self.is_bot_player = [False] * self.num_players

        for i in range(self.num_real_players, self.num_players):
            self.is_bot_player[i] = True

        self.player_colors = ["Red", "Blue", "Yellow", "Green"]
        self.turns_bg_color_list = ["red", "blue", "yellow", "green"]
        self.turns_fg_color_list = ["white", "white", "black", "white"]
        self.tile_1_position = [5, 630]
        # calling the simpledialog window.
        mydialog(self.root)
        # frame within root
        self.window = tk.Frame(self.root,bg="#BEE9E4")
        self.window.pack()
        # Coordinates of certain tiles containing end points of ladders and snakes in the canvas 'canvas1'.
        self.tile_coords_map = {2:[75,630], 7:[425,630], 22:[75,490], 23:[145,490], 28:[495,490], 29:[565,490], 30:[635,490],
                        32:[565,420], 41:[5,350], 44:[215,350], 54:[425,280], 58:[145,280], 69:[565,210], 70:[635,210],
                        74:[425,140], 77:[215,140], 80:[5,140], 83:[145,70], 90:[635,70], 92:[565,0], 5:[285,630],
                        3:[145,630], 34:[425,420], 46:[355,350], 24:[215,490], 12:[565,560], 63:[145,210], 67:[425,210],
                        86:[355,70], 25:[285,490],
                        # Add coordinates for power-up tiles
                        15:[350,560],  # Shield power-up
                        45:[285,350],  # Double move power-up
                        75:[495,140]}  # Teleport power-up
        # Mapping tile number to the next tile up to reach using ladder. Keys are ladder basement, values are top level of ladder.
        self.ladders_map = {2:23,7:29,22:41,28:77,30:32,44:58,54:69,70:90,74:92,80:83}
        # Mapping tile number to the downward tile to go down using snake. Keys are snake heads, values are snake tails.
        self.snakes_map = {27:7,35:5,39:3,50:34,59:46,66:24,73:12,76:63,89:67,97:86,99:25}
        # images converted to PhotoImage variables.
        self.board_image = tk.PhotoImage(file="assets/images/board.png")
        self.face1 = tk.PhotoImage(file="assets/images/faces-one.png")
        self.face2 = tk.PhotoImage(file="assets/images/faces-two.png")
        self.face3 = tk.PhotoImage(file="assets/images/faces-three.png")
        self.face4 = tk.PhotoImage(file="assets/images/faces-four.png")
        self.face5 = tk.PhotoImage(file="assets/images/faces-five.png")
        self.face6 = tk.PhotoImage(file="assets/images/faces-six.png")
        self.player_red = tk.PhotoImage(file="assets/images/player1_red_piece.png")
        self.player_blue = tk.PhotoImage(file="assets/images/player2_blue_piece.png")
        self.player_yellow = tk.PhotoImage(file="assets/images/player3_yellow_piece.png")
        self.player_green = tk.PhotoImage(file="assets/images/player4_green_piece.png")
        self.exit_button_image = tk.PhotoImage(file="assets/images/exit_wooden_board.png").subsample(2,2)
        self.play_again_image = tk.PhotoImage(file="assets/images/play-again-button2.png").subsample(2,2)
        self.sound_on_image = tk.PhotoImage(file="assets/images/sound_on_button.png")
        self.sound_off_image = tk.PhotoImage(file="assets/images/sound_off_button.png")
        self.winner_board_image = tk.PhotoImage(file="assets/images/winner_board.png").subsample(2,2)
        self.winner_red = tk.PhotoImage(file="assets/images/winner_red.png")
        self.winner_blue = tk.PhotoImage(file="assets/images/winner_blue.png")
        self.winner_yellow = tk.PhotoImage(file="assets/images/winner_yellow.png")
        self.winner_green = tk.PhotoImage(file="assets/images/winner_green.png")
        self.app_icon_image = tk.PhotoImage(file="assets/images/snakesAndLaddersIcon.png")
        self.about_icon_image = tk.PhotoImage(file="assets/images/info-100.png").subsample(2,2)
        self.winner_images_list = [self.winner_red,self.winner_blue,self.winner_yellow,self.winner_green]
        self.dice_faces_images = [self.face1,self.face2,self.face3,self.face4,self.face5,self.face6]
        # Left side frame
        self.frameLeft = tk.Frame(self.window,bg="#BEE9E4")
        self.frameLeft.grid(row=0,column=0)
        tk.Label(self.frameLeft,text="Players",font=("Comic Sans MS",25),bg="#BEE9E4").pack()
        self.display_players = tk.Frame(self.frameLeft,bg="#BEE9E4")
        self.display_players.pack()
        tk.Label(self.display_players,image=self.player_red,bg="#BEE9E4").grid(row=0,column=0,padx=5)
        tk.Label(self.display_players,image=self.player_blue,bg="#BEE9E4").grid(row=0,column=1)
        # Winner label is empty
        self.winner_label = tk.Label(self.frameLeft,image=self.winner_board_image,bg="#BEE9E4")
        self.winner_label.pack(pady=20)
        # Turns to display who is the next player to roll the dice
        self.turns = tk.Label(self.frameLeft,text="Next turn:RED",font=("Arial",13),width=20,bg="red",fg="white",pady=10)
        self.turns.pack(padx=81)
        # center frame to hold canvas and player pieces
        self.frameCenter = tk.Frame(self.window,bg="#BEE9E4")
        self.frameCenter.grid(row=0,column=1)
        # Frame right
        self.frameRight = tk.Frame(self.window,bg="#BEE9E4")
        self.frameRight.grid(row=0,column=2)
        # canvas created to contain board picture
        self.canvas1 = tk.Canvas(self.frameCenter,width=700,height=900,bg="#BEE9E4",highlightthickness=0)
        self.canvas1.pack(pady=15)
        # board is placed on canvas
        self.board_canvas = self.canvas1.create_image(0,20,image=self.board_image,anchor=tk.NW)
        self.player_red_canvas = self.canvas1.create_image(5,710,image=self.player_red,anchor=tk.NW)
        self.player_blue_canvas = self.canvas1.create_image(100,710,image=self.player_blue,anchor=tk.NW)
        self.player_yellow_canvas = self.canvas1.create_image(180,710,image=self.player_yellow,anchor=tk.NW,state="hidden")
        self.player_green_canvas = self.canvas1.create_image(250,710,image=self.player_green,anchor=tk.NW,state="hidden")
        self.players_canvas_list = [self.player_red_canvas,self.player_blue_canvas] # append yellowpiece to this array
        if self.num_players==3: # When the number of players selected is 3
            self.add_3_player_game()
        elif self.num_players==4: # When the number of players selected is 4
            self.add_4_player_game()
        # Exit button
        self.inner_frame = tk.Frame(self.frameRight,bg="#BEE9E4")
        self.inner_frame.pack()
        self.exit_button = tk.Button(self.inner_frame,text="Exit",font=("Arial",17),bd=0,command=self.exit_game,fg="white",image=self.exit_button_image,bg="#BEE9E4",activebackground="#BEE9E4")
        self.exit_button.grid(row=0,column=0,pady=10)
        self.about_button = tk.Button(self.inner_frame,text="Info",bg="#BEE9E4",image=self.about_icon_image,bd=0,activebackground="#BEE9E4",command=self.show_info)
        self.about_button.grid(row=0,column=1,padx=15)
        # Play again button
        self.play_again_button = tk.Button(self.frameRight,text="Play again",bd=0,font=("Arial",20),command=self.play_game_again,image=self.play_again_image,bg="#BEE9E4",activebackground="#BEE9E4",state=tk.DISABLED)
        self.play_again_button.pack(pady=10)
        # sound on/off button
        self.sound_button = tk.Button(self.frameRight,image=self.sound_on_image,bd=0,bg="#BEE9E4",activebackground="#BEE9E4",command=self.turn_sound_on_off)
        self.sound_button.pack(pady=5)
        # dice face
        self.dice_label = tk.Label(self.frameRight,image=self.face3)
        self.dice_label.pack(pady=10)
        # roll dice button
        self.button1 = tk.Button(self.frameRight,text="Roll dice",font=("Arial",20),bg="black",fg="white",command=self.thread_roll_dice,activebackground="black",activeforeground="yellow")
        self.button1.pack(padx=100,pady=25)

        # Add power-up display label after frameRight is created
        self.power_up_label = tk.Label(self.frameRight, 
                                     text="No active power-ups",
                                     font=("Arial", 12),
                                     bg="#BEE9E4")
        self.power_up_label.pack(pady=5)

        # Add power-up images
        try:
            self.shield_image = tk.PhotoImage(file="assets/images/shield.png")
            self.double_move_image = tk.PhotoImage(file="assets/images/double.png")
            self.teleport_image = tk.PhotoImage(file="assets/images/teleport.png")
        except tk.TclError:
            print("Warning: Power-up images not found. Using text-only display.")

        try:
            self.shield_image = tk.PhotoImage(file="assets/images/shield.png").subsample(2, 2)  # Make images smaller
            self.double_move_image = tk.PhotoImage(file="assets/images/double.png").subsample(2, 2)
            self.teleport_image = tk.PhotoImage(file="assets/images/teleport.png").subsample(2, 2)
            self.create_power_up_images()
        except tk.TclError as e:
            print(f"Warning: Power-up images not found. Error: {e}")    

        # Key events
        # Escape key to exit full screen.

        self.root.bind("<Escape>", self.exit_full_screen)
        self.root.bind("<f>", self.open_full_screen)
        self.root.bind("<F>", self.open_full_screen)
        self.root.bind("<space>", self.thread_key_roll_dice)

        self.root.mainloop()

    # Function to play the sound of dice rolling
    def play_dice_audio(self):
        global all_sound_active
        if self.all_sound_active == True:
            mixer.init()
            mixer.music.load("assets/sounds/dice-142528.mp3")
            mixer.music.set_volume(0.6)
            mixer.music.play()

    def thread_play_dice_sound(self):
        thread_var = Thread(target=self.play_dice_audio())
        thread_var.start()

    def play_click_sound(self):
        global all_sound_active
        if self.all_sound_active == True:
            mixer.init()
            mixer.music.load("assets/sounds/mixkit-classic-click-1117.wav")
            mixer.music.set_volume(0.6)
            mixer.music.play()

    def thread_play_click_sound(self):
        thread_var = Thread(target=self.play_click_sound())
        thread_var.start()

    def play_ladder_up_audio(self):
        global all_sound_active
        if self.all_sound_active == True:
            mixer.init()
            mixer.music.load("assets/sounds/zapsplat_cartoon_climb_ascend_ladder_short_high_pitched_lite_001_44028.mp3")
            mixer.music.set_volume(0.5)
            mixer.music.play()

    def thread_play_ladder_up_sound(self):
        thread_var = Thread(target=self.play_ladder_up_audio())
        thread_var.start()

    def play_snake_down_audio(self):
        global all_sound_active
        if self.all_sound_active == True:
            mixer.init()
            mixer.music.load("assets/sounds/Blastwave_FX_SnakeHiss_SEU04.2.mp3")
            mixer.music.set_volume(0.5)
            mixer.music.play()

    def thread_play_snake_down_sound(self):
        thread_var = Thread(target=self.play_snake_down_audio())
        thread_var.start()

    def play_gameover_audio(self):
        global all_sound_active
        if self.all_sound_active == True:
            mixer.init()
            mixer.music.load("assets/sounds/game-over-160612.mp3")
            mixer.music.set_volume(0.5)
            mixer.music.play()

    def thread_play_gameover_sound(self):
        thread_var = Thread(target=self.play_gameover_audio())
        thread_var.start()

    def roll_dice(self):
        if self.currentPlayer >= len(self.players):
            self.currentPlayer = 0
        self.thread_play_dice_sound()
        dice_face_value = random.randint(1, 6)
        self.dice_label.config(image=self.dice_faces_images[dice_face_value - 1])

        if not self.check_player_status(self.currentPlayer) and dice_face_value == 1:
            self.change_player_status(self.currentPlayer)

        if self.activePlayers[self.currentPlayer]:
            self.disable_rolling_dice()
            if self.player_tile_positions[self.currentPlayer] + dice_face_value <= 100:
                oldValue = self.player_tile_positions[self.currentPlayer]
                self.player_tile_positions[self.currentPlayer] += dice_face_value
                newValue = self.player_tile_positions[self.currentPlayer]
                canvas_piece = self.players_canvas_list[self.currentPlayer]
                
                # Move player to new position
                if newValue == 1:
                    self.canvas1.moveto(canvas_piece, self.tile_1_position[0], self.tile_1_position[1])
                else:
                    for num in range(oldValue, newValue):
                        if num % 10 == 0:
                            self.move_up(canvas_piece)
                        else:
                            if num < 10 or int(str(num)[0]) % 2 == 0:
                                self.move_Right(canvas_piece)
                            else:
                                self.move_left(canvas_piece)
                        time.sleep(0.03)
                
                # Check for power-ups (fixed indentation)
                if newValue in self.power_up_tiles:
                    power_up = self.power_up_tiles[newValue]
                    self.handle_power_up(power_up)
                    # Remove power-up from the board
                    for item in self.canvas1.find_overlapping(
                        self.tile_coords_map[newValue][0],
                        self.tile_coords_map[newValue][1],
                        self.tile_coords_map[newValue][0] + 70,
                        self.tile_coords_map[newValue][1] + 70
                    ):
                        if item > self.player_green_canvas:  # Only delete power-up images
                            self.canvas1.delete(item)
                    self.power_up_tiles.pop(newValue)
                    self.update_power_up_display()
                
                # Check for snakes - but first check if player has shield
                if newValue in self.snakes_map:
                    if "shield" in self.player_power_ups[self.currentPlayer]:
                        self.player_power_ups[self.currentPlayer].remove("shield")
                        self.update_power_up_display()
                        messagebox.showinfo("Shield Used!", "Your shield protected you from the snake!")
                    else:
                        self.thread_play_snake_down_sound()
                        snake_tail = self.snakes_map[newValue]
                        self.player_tile_positions[self.currentPlayer] = snake_tail
                        if snake_tail in self.tile_coords_map:
                            self.canvas1.coords(canvas_piece, 
                                             self.tile_coords_map[snake_tail][0], 
                                             self.tile_coords_map[snake_tail][1])
                
                # Check for ladders
                elif newValue in self.ladders_map:
                    self.thread_play_ladder_up_sound()
                    ladder_top = self.ladders_map[newValue]
                    self.player_tile_positions[self.currentPlayer] = ladder_top
                    if ladder_top in self.tile_coords_map:
                        self.canvas1.coords(canvas_piece, 
                                         self.tile_coords_map[ladder_top][0], 
                                         self.tile_coords_map[ladder_top][1])
                
                # Check for winner
                if self.player_tile_positions[self.currentPlayer] == 100:
                    self.winner = True
                    self.winner_label.config(image=self.winner_images_list[self.currentPlayer])
                    self.thread_play_gameover_sound()
                    self.play_again_button.config(state=tk.NORMAL)
                    self.disable_rolling_dice()
                    return

        if not self.winner:
            self.thread_activate_rolling_dice()

        if dice_face_value != 6:
            self.currentPlayer = (self.currentPlayer + 1) % self.num_players  
            self.bonus_active = False
        else:
            self.bonus_active = True

        if self.currentPlayer >= len(self.players):
            self.currentPlayer = 0

        self.turns.config(
            text=f"Next turn: {self.player_colors[self.currentPlayer]}",
            bg=self.turns_bg_color_list[self.currentPlayer],
            fg=self.turns_fg_color_list[self.currentPlayer])

        if not self.winner and self.is_bot_player[self.currentPlayer]:
            self.root.after(1000, self.thread_roll_dice)

    def move_Right(self, canvas_item):
        self.canvas1.move(canvas_item, 70, 0)
        self.root.update()
        time.sleep(0.05)

    def move_left(self, canvas_item):
        self.canvas1.move(canvas_item, -70, 0)
        self.root.update()
        time.sleep(0.04)

    def move_up(self, canvas_item):
        self.canvas1.move(canvas_item, 0, -70)
        self.root.update()
        time.sleep(0.04)

    def thread_roll_dice(self):
        stack_size(200000000)
        thread_var = Thread(target=self.roll_dice)
        thread_var.start()

    def thread_key_roll_dice(self, event):
        stack_size(200000000)
        thread_var = Thread(target=self.roll_dice)
        thread_var.start()

    def disable_rolling_dice(self):
        self.button1.config(state=tk.DISABLED)
        self.root.unbind("<space>")

    def activate_rolling_dice(self):
        self.button1.config(state=tk.NORMAL)
        self.root.bind("<space>", self.thread_key_roll_dice)

    def thread_activate_rolling_dice(self):
        thread_var = Thread(target=self.activate_rolling_dice)
        thread_var.start()

    def check_player_status(self, playerNumber):
        return self.activePlayers[playerNumber]

    def change_player_status(self, playerNumber):
        self.activePlayers[playerNumber] = True

    def exit_full_screen(self, event):
        self.root.attributes('-fullscreen', False)

    def open_full_screen(self, event):
        self.root.attributes('-fullscreen', True)

    # Function to start the game with three players (Red, Blue, Yellow).
    def add_3_player_game(self):
        self.players.append(2)
        self.activePlayers.append(False)
        self.player_tile_positions.append(0)
        self.is_bot_player.append(self.num_real_players <= 2)
        self.canvas1.itemconfig(self.player_yellow_canvas, state="normal")
        self.players_canvas_list.append(self.player_yellow_canvas)
        tk.Label(self.display_players, image=self.player_yellow, bg="#BEE9E4").grid(row=0, column=2)

    def add_4_player_game(self):
        self.players.append(2)
        self.players.append(3)
        self.activePlayers.extend([False, False])
        self.player_tile_positions.extend([0, 0])
        self.is_bot_player.append(self.num_real_players <= 2)
        self.is_bot_player.append(self.num_real_players <= 3)
        self.canvas1.itemconfig(self.player_yellow_canvas, state="normal")
        self.canvas1.itemconfig(self.player_green_canvas, state="normal")
        self.players_canvas_list.append(self.player_yellow_canvas)
        self.players_canvas_list.append(self.player_green_canvas)
        tk.Label(self.display_players, image=self.player_yellow, bg="#BEE9E4").grid(row=0, column=2)
        tk.Label(self.display_players, image=self.player_green, bg="#BEE9E4").grid(row=0, column=3)



    # Function to restart the game again from the beginning by resetting player pieces to its initial coordinates.
    def play_game_again(self):
        global winner, currentPlayer
        self.thread_play_click_sound()
        self.play_again_button.config(state=tk.DISABLED)
        for ptr in range(0, len(self.player_tile_positions)):
            self.player_tile_positions[ptr] = 0
        for ptr in range(0, len(self.activePlayers)):
            self.activePlayers[ptr] = False
        self.canvas1.coords(self.player_red_canvas, 5, 710)
        self.canvas1.coords(self.player_blue_canvas, 100, 710)
        self.canvas1.coords(self.player_yellow_canvas, 180, 710)
        self.canvas1.coords(self.player_green_canvas, 250, 710)
        self.activate_rolling_dice()
        self.winner = False
        self.currentPlayer = 0
        self.turns.config(text="Next:RED", bg="red", fg="white")
        self.winner_label.config(image=self.winner_board_image)

    # Function to exit the game on button 'exit_button'.
    def exit_game(self):
        self.thread_play_click_sound()
        if messagebox.askyesno("Quit game?", "Do you really want to quit the game now?") == True:
            self.root.destroy()

    # Function to turn the sound ON or MUTE
    def turn_sound_on_off(self):
        self.all_sound_active = not (self.all_sound_active)
        if not self.all_sound_active:
            self.sound_button.config(image=self.sound_off_image)
        else:
            self.thread_play_click_sound()
            self.sound_button.config(image=self.sound_on_image)

    def show_info(self):
        info_window = tk.Toplevel(self.root)
        info_window.title("About Snake and Ladders")
        info_window.geometry("600x400")
        info_window.config(bg="#eb2f06")
        
        # Project Title
        title_label = tk.Label(info_window, 
                            text="AI-Enhanced Snake and Ladders",
                            font=("Times New Roman", 24, "bold"),
                            bg="#eb2f06",
                            fg="white")
        title_label.pack(pady=20)
        
        # Project Description
        description = """
        An intelligent implementation of the classic Snake and Ladders game
        featuring AI opponents and smart game mechanics.
        
        Key Features:
        • Intelligent AI opponents with strategic gameplay
        • Multi-player support (2-4 players)
        • Interactive dice rolling system
        • Dynamic snake and ladder animations
        • Sound effects and visual feedback
        • Fullscreen gaming experience
        
        Project developed for Artificial Intelligence Lab
        Submitted to: Sir Shafique ur Rehman
        
        Developers:
        • Muhammad Omer Khan [22k-4418]
        • Muhib Siddiqui [22k-4428]
        • Salik Ahmed [22k-4403]
        
        FAST-NUCES, Karachi Campus
        Spring 2024
        """
        
        desc_label = tk.Label(info_window,
                            text=description,
                            font=("Times New Roman", 14),
                            bg="#eb2f06",
                            fg="white",
                            justify=tk.LEFT)
        desc_label.pack(pady=20)
        
        # Close button
        close_button = tk.Button(info_window,
                                text="Close",
                                command=info_window.destroy,
                                font=("Comic Sans MS", 12),
                                bg="black",
                                fg="white",
                                activebackground="brown")
        close_button.pack(pady=10)
        
        # Center the window
        info_window.transient(self.root)
        info_window.grab_set()
        info_window.wait_window()

    def handle_power_up(self, power_up):
        """Handle different power-ups"""
        if power_up == "shield":
            self.player_power_ups[self.currentPlayer].append("shield")
            messagebox.showinfo("Power Up!", "You got a shield! It will protect you from one snake.")
            
        elif power_up == "double_move":
            self.bonus_active = True
            messagebox.showinfo("Power Up!", "You got a double move! Roll again!")
            
        elif power_up == "teleport":
            self.handle_teleport()
        
        self.update_power_up_display()

    def handle_teleport(self):
        """Handle teleport power-up"""
        current_pos = self.player_tile_positions[self.currentPlayer]
        valid_positions = [pos for pos in range(current_pos + 1, min(current_pos + 11, 101))
                         if pos not in self.snakes_map]
        
        if valid_positions:
            new_pos = random.choice(valid_positions)
            canvas_piece = self.players_canvas_list[self.currentPlayer]
            self.player_tile_positions[self.currentPlayer] = new_pos
            
            if new_pos in self.tile_coords_map:
                self.canvas1.coords(canvas_piece, 
                                 self.tile_coords_map[new_pos][0], 
                                 self.tile_coords_map[new_pos][1])
            
            messagebox.showinfo("Teleport!", f"You teleported to position {new_pos}!")

    def update_power_up_display(self):
        """Update the display of active power-ups"""
        power_ups = self.player_power_ups[self.currentPlayer]
        power_up_text = "Active Power-ups: " + ", ".join(power_ups) if power_ups else "No active power-ups"
        self.power_up_label.config(text=power_up_text)


SnakesandLadders()