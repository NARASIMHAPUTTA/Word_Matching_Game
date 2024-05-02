import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import pygame
import random
from random_word import RandomWords

class BaseMenu:

    def __init__(self, master):
        self.master = master
        self.loading_label = None
        self.start_button = None
        self.exit_button = None
        
        self.create_widgets()
        self.play_menu_sound()

    def create_widgets(self):
        img = Image.open("1.jpg")
        img = img.resize((800, 600), Image.BICUBIC)
        self.background_image = ImageTk.PhotoImage(img)  

        self.background_label = tk.Label(self.master, image=self.background_image)
        self.background_label.place(x=0, y=0, relwidth=1, relheight=1)

        self.start_button = tk.Button(self.master, text="Start", command=self.start_game, bg="#0C4674", fg="white", font=("Cascadia Mono", 14))
        self.start_button.place(relx=0.46, rely=0.65, anchor="center")

        self.exit_button = tk.Button(self.master, text="Exit", command=self.master.quit, bg="#D94462", fg="white", font=("Cascadia Mono", 14))
        self.exit_button.place(relx=0.60, rely=0.65, anchor="center")

    def play_menu_sound(self):
        pygame.mixer.init()
        pygame.mixer.music.load("game_sounds/menu.mp3")
        pygame.mixer.music.play()

    def start_game(self):
        self.start_button.place_forget()
        self.exit_button.place_forget()

        self.loading_label = tk.Label(self.master, text="Loading...", font=("Arial", 20), fg="white", bg="black", bd=0)
        self.loading_label.place(relx=0.5, rely=0.5, anchor="center")
        self.master.after(3000, self.create_game)

    def create_game(self):
        if self.loading_label:
            self.loading_label.destroy()
        max_score = 10
        time_limit = 180
        
        game = WordMatchingGame(self.master, self, max_score, time_limit)
        game.create_widgets()
        self.play_background_music()

    def play_background_music(self):
        pygame.mixer.music.load("game_sounds/background_music.mp3")
        pygame.mixer.music.play(-1)


class FrontMenu(BaseMenu):
    def __init__(self, master):
        super().__init__(master)

class BackMenu(BaseMenu):
    def __init__(self, master, front_menu):
        super().__init__(master)
        self.front_menu = front_menu

    def create_widgets(self):
        super().create_widgets()

        self.start_button.config(text="Play Again", command=self.restart_game)

    def restart_game(self):
        self.start_button.place_forget()
        self.exit_button.place_forget()

        self.loading_label = tk.Label(self.master, text="Loading...", font=("Arial", 20), fg="white", bg="black", bd=0)
        self.loading_label.place(relx=0.5, rely=0.5, anchor="center")
        self.master.after(3000, self.create_game)

    def create_game(self):
        if self.loading_label:
            self.loading_label.destroy()
        max_score = 10
        time_limit = 180
        
        game = WordMatchingGame(self.master, self.front_menu, max_score, time_limit)
        game.create_widgets()
        self.play_background_music()


class WordMatchingGame:
    
    def __init__(self, master, front_menu, max_score, time_limit):
        self.master = master
        self.front_menu = front_menu
        self.max_score = max_score
        self.time_limit = time_limit
        self.matched_pairs = 0
        self.selected_cards = []
        self.grid_frame = None
        self.create_widgets()
        self.start_time = time_limit
        self.timer_id = None
        self.update_timer()
        self.create_grid()

    def create_widgets(self):
        self.grid_frame = tk.Frame(self.master)
        self.grid_frame.place(relx=0.5, rely=0.5, anchor="center")
        self.timer_label = tk.Label(self.master, text="", font=("Arial", 14))
        self.timer_label.place(relx=0.5, rely=0.1, anchor="center")

        self.restart_button = tk.Button(self.master, text="Restart", command=self.restart_game, bg="lightblue", font=("Arial", 12))
        self.restart_button.place(relx=0.1, rely=0.9, anchor="center")

        self.exit_button = tk.Button(self.master, text="Exit", command=self.master.quit, bg="salmon", font=("Arial", 12))
        self.exit_button.place(relx=0.9, rely=0.9, anchor="center")

        self.score_label = tk.Label(self.master, text="Score: 0 / {}".format(self.max_score), font=("Arial", 14))
        self.score_label.place(relx=0.5, rely=0.2, anchor="center")

    def restart_game(self):
        self.matched_pairs = 0
        self.update_score_label()
        self.update_timer()
        self.create_grid()


    def create_grid(self):
        for card in self.grid_frame.winfo_children():
            card.grid_forget()
        words = self.generate_word_grid()
        self.cards = []
        for i in range(5):
            for j in range(6):
                word = words[i][j]
                card = tk.Label(self.grid_frame, text=word, relief="raised", width=10, height=2, bg="lightblue", font=("Arial", 14))
                card.grid(row=i, column=j, padx=5, pady=5)
                card.bind("<Button-1>", self.flip_card)
                self.cards.append(card)


    def generate_word_grid(self):
        r = RandomWords()
        
        all_words = [r.get_random_word() for _ in range(30)]
        
        unique_words = list(set(all_words))
        
        matching_words = random.sample(unique_words, k=min(10, len(unique_words) // 2))
        
        matching_pairs = matching_words * 2
        
        random.shuffle(matching_pairs)
        
        remaining_words = [word for word in unique_words if word not in matching_words]
        
        additional_words = random.sample(remaining_words, k=30 - len(matching_pairs))
        
        words = matching_pairs + additional_words
        
        random.shuffle(words)
        
        words_grid = [words[i:i + 6] for i in range(0, 30, 6)]
        
        return words_grid


    def update_score_label(self):
        self.score_label.config(text="Score: {} / {}".format(self.matched_pairs, self.max_score))
        

    def update_timer(self):
        
        self.start_time = self.time_limit
        self.update_timer_display()
        

    def update_timer_display(self):
        
        if self.start_time >= 0 and self.matched_pairs < self.max_score:
            minutes, seconds = divmod(self.start_time, 60)
            self.timer_label.config(text="Time Left: {:02d}:{:02d}".format(minutes, seconds))
            self.start_time -= 1
            self.master.after(1000, self.update_timer_display)
            
        elif self.matched_pairs == self.max_score:
            self.game_won()
            
        else:
            self.game_over()

    def flip_card(self, event):
        
        card = event.widget
        
        if card["state"] != "disabled":
            
            card_index = self.cards.index(card)
            word = card["text"]
            
            if card_index not in [index for index, _ in self.selected_cards]:
                card.config(bg="lightgreen")
                self.selected_cards.append((card_index, word))
                
                if len(self.selected_cards) == 2:
                    self.check_match()
                    
            else:
                self.selected_cards = [(index, word) for index, word in self.selected_cards if index != card_index]
                card.config(bg="lightblue")


    def check_match(self):
        indices, words = zip(*self.selected_cards)
        
        if len(set(words)) == 1:
            self.matched_pairs += 1
            self.update_score_label()
            self.remove_matched_words()
            self.show_alert()
            self.master.after(1000, lambda: self.turn_to_yellow(indices))
        else:
            self.turn_to_red(indices)

    def turn_to_yellow(self, indices):
        for index in indices:
            self.cards[index].config(bg="gold")
        self.master.after(1000, lambda: self.flip_matched_cards(indices))

    def flip_matched_cards(self, indices):
        for index in indices:
            self.cards[index].config(text="", bg="lightblue")
        self.selected_cards = []

    def turn_to_red(self, indices):
        for index in indices:
            self.cards[index].config(bg="red")
        self.master.after(1000, lambda: self.reset_cards(indices))

    def reset_cards(self, indices):
        for index in indices:
            self.cards[index].config(bg="lightblue")
        self.selected_cards = []

    def remove_matched_words(self):
        for index, _ in self.selected_cards:
            self.cards[index].config(state="disabled")

    def show_alert(self):
        alert_label = tk.Label(self.master, text="Matched words!", font=("Arial", 20), fg="red")
        alert_label.place(relx=0.5, rely=0.1, anchor="center")
        self.master.after(2000, alert_label.destroy)

    def game_won(self):
        pygame.mixer.init()  
        pygame.mixer.music.load("game_sounds/win.mp3")
        pygame.mixer.music.play()
        messagebox.showinfo("you have!", "Game won!")
        self.front_menu.back_menu = BackMenu(self.master, self.front_menu)

    def game_over(self):
        messagebox.showinfo("Time's Up!", "Game Over!")


def main():
    root = tk.Tk()
    root.title("Word Matching Game - Front Menu")
    root.geometry("800x600")
    root.minsize(400, 300)
    front_menu = FrontMenu(root)
    root.mainloop()

if __name__ == "__main__":
    main()