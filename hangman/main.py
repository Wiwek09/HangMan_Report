import tkinter as tk
from tkinter import messagebox
from engine import HangmanGame

class Hangman:
    def __init__(self, root):
        self.root = root
        self.root.title("Hangman Game")

        # start a new game
        self.game = HangmanGame(level="basic")

        # Timer setup
        self.time_left = 15
        self.timer_var = tk.StringVar()
        self.timer_label = tk.Label(root, textvariable=self.timer_var, font=("Arial", 12), fg="red")
        self.timer_label.pack(pady=5)

        # Canvas for hangman drawing
        self.canvas = tk.Canvas(root, width=300, height=300, bg="white")
        self.canvas.pack(pady=20)

        # Word display (masked, spaced)
        self.word_var = tk.StringVar()
        self.word_label = tk.Label(root, textvariable=self.word_var, font=("Courier", 20))
        self.word_label.pack(pady=10)

        # Entry for guessing letters
        self.entry = tk.Entry(root, font=("Arial", 14))
        self.entry.pack()
        self.entry.bind("<Return>", self.make_guess)

        # Status message
        self.msg_var = tk.StringVar()
        self.msg_label = tk.Label(root, textvariable=self.msg_var, fg="blue")
        self.msg_label.pack(pady=5)

        # Restart button
        self.restart_btn = tk.Button(root, text="Restart", command=self.restart)
        self.restart_btn.pack(pady=10)

        # draw initial state + start timer
        self.update_display()
        self.start_timer()

    def draw_hangman(self):
        """Draw hangman parts depending on lives left."""
        self.canvas.delete("all")

        # base
        self.canvas.create_line(20, 280, 280, 280, width=3)
        self.canvas.create_line(60, 280, 60, 40, width=3)
        self.canvas.create_line(60, 40, 200, 40, width=3)
        self.canvas.create_line(200, 40, 200, 70, width=3)

        parts = 6 - self.game.remaining_lives

        if parts >= 1:  # head
            self.canvas.create_oval(180, 70, 220, 110, width=3)
        if parts >= 2:  # body
            self.canvas.create_line(200, 110, 200, 180, width=3)
        if parts >= 3:  # left arm
            self.canvas.create_line(200, 130, 170, 160, width=3)
        if parts >= 4:  # right arm
            self.canvas.create_line(200, 130, 230, 160, width=3)
        if parts >= 5:  # left leg
            self.canvas.create_line(200, 180, 170, 220, width=3)
        if parts >= 6:  # right leg
            self.canvas.create_line(200, 180, 230, 220, width=3)

    def update_display(self):
        # Always show spaced underscores or letters
        spaced_display = " ".join(self.game.display)
        self.word_var.set(spaced_display)
        self.draw_hangman()

    def make_guess(self, event=None):
        guess = self.entry.get().strip().lower()
        self.entry.delete(0, tk.END)
        result = self.game.guess(guess)

        if result["status"] == "invalid":
            self.msg_var.set("Enter a single A-Z letter.")
        elif result["status"] == "repeat":
            self.msg_var.set("Already guessed!")
        elif result["status"] == "hit":
            self.msg_var.set("Good guess!")
        elif result["status"] == "miss":
            self.msg_var.set("Wrong guess!")

        # reset timer after a valid attempt
        self.time_left = 15
        self.update_display()

        if self.game.is_over():
            if self.game.is_won():
                messagebox.showinfo("You Won!", f"🎉 The answer was: {self.game.answer}")
            else:
                messagebox.showerror("Game Over", f"💀 The answer was: {self.game.answer}")
            self.restart()

    def start_timer(self):
         # Stop updating timer if game is finished
        if self.game.is_over():  
            return 
        """Start or continue the countdown timer."""
        if self.time_left > 0:
            self.timer_var.set(f"Time left: {self.time_left} sec")
            self.time_left -= 1
            self.root.after(1000, self.start_timer)
        else:
            # Time ran out -> lose a life
            self.game.deduct_life()
            self.msg_var.set("Time’s up! Life lost.")
            self.time_left = 15  # reset timer
            self.update_display()
            if self.game.is_over():
                messagebox.showerror("Game Over", f"The answer was: {self.game.answer}")
                self.restart()
            else:
                self.start_timer()  # continue countdown for next round

    def restart(self):
        self.game.reset()
        self.msg_var.set("")
        self.time_left = 15
        self.update_display()
        self.start_timer()

if __name__ == "__main__":
    root = tk.Tk()
    app = Hangman(root)
    root.mainloop()
