import tkinter as tk
from tkinter import messagebox
import random

# ---------------------- Gale‑Shapley core ----------------------
def gale_shapley_step(males, females, male_prefs, female_prefs, engagements, next_proposal, free_males):
    """
    Perform ONE round (all free males propose once) and return:
      - updated engagements
      - updated next_proposal
      - updated free_males
      - a list of event strings for this round
    """
    if not free_males:
        return engagements, next_proposal, free_males, []

    events = []
    new_free = []

    for male in free_males:
        pref_list = male_prefs[male]
        if next_proposal[male] >= len(pref_list):
            continue
        female = pref_list[next_proposal[male]]
        next_proposal[male] += 1

        event = f"{male} proposes to {female}"

        if female not in engagements:
            engagements[female] = male
            event += f" → {female} accepts (was free)"
        else:
            current_male = engagements[female]
            # rank = position in female's preference list (lower is better)
            rank_new = female_prefs[female].index(male)
            rank_curr = female_prefs[female].index(current_male)
            if rank_new < rank_curr:
                engagements[female] = male
                event += f" → {female} switches (prefers {male})"
                new_free.append(current_male)
            else:
                event += f" → {female} rejects (prefers {current_male})"
                new_free.append(male)
        events.append(event)

    free_males[:] = new_free
    return engagements, next_proposal, free_males, events

# ---------------------- GUI Application ----------------------
class GaleShapleyGame:
    def __init__(self, root):
        self.root = root
        self.root.title("Gale‑Shapley Stable Marriage Game")
        self.root.geometry("1000x700")
        self.root.configure(bg="#f0f0f0")

        # ---------- Simulation data ----------
        self.n = 10
        self.males = [f"M{i+1}" for i in range(self.n)]
        self.females = [f"F{i+1}" for i in range(self.n)]

        # Generate random preferences
        random.seed()
        self.male_prefs = self._gen_prefs(self.males, self.females)
        self.female_prefs = self._gen_prefs(self.females, self.males)

        # State for algorithm
        self.engagements = {}          # female -> male
        self.next_proposal = {m: 0 for m in self.males}
        self.free_males = list(self.males)
        self.round = 0
        self.finished = False

        # Betting
        self.bet_pair = None          # (male, female)
        self.bet_placed = False

        # ---------- Build UI ----------
        # Top frame: betting controls
        top_frame = tk.Frame(root, bg="#f0f0f0", pady=10)
        top_frame.pack(fill=tk.X)

        tk.Label(top_frame, text="Place your bet:", font=("Arial", 12, "bold"), bg="#f0f0f0").pack(side=tk.LEFT, padx=10)
        self.male_var = tk.StringVar()
        self.female_var = tk.StringVar()
        male_menu = tk.OptionMenu(top_frame, self.male_var, *self.males)
        female_menu = tk.OptionMenu(top_frame, self.female_var, *self.females)
        male_menu.config(width=5)
        female_menu.config(width=5)
        male_menu.pack(side=tk.LEFT, padx=5)
        female_menu.pack(side=tk.LEFT, padx=5)

        self.bet_btn = tk.Button(top_frame, text="Place Bet", command=self.place_bet, bg="#ffcc00", font=("Arial", 10, "bold"))
        self.bet_btn.pack(side=tk.LEFT, padx=10)

        self.bet_label = tk.Label(top_frame, text="No bet placed", font=("Arial", 10), bg="#f0f0f0", fg="blue")
        self.bet_label.pack(side=tk.LEFT, padx=20)

        # Next round button
        self.next_btn = tk.Button(root, text="➡️ Next Round", command=self.next_round, bg="#4CAF50", fg="white",
                                  font=("Arial", 12, "bold"), padx=20, pady=5)
        self.next_btn.pack(pady=10)

        # Info label
        self.info_label = tk.Label(root, text="Round 0 - No matches yet", font=("Arial", 10), bg="#f0f0f0", fg="gray")
        self.info_label.pack()

        # Canvas for drawing connections (left/right lists)
        canvas_frame = tk.Frame(root, bg="#f0f0f0")
        canvas_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        self.canvas = tk.Canvas(canvas_frame, bg="white", highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True)

        # Bind resize event to redraw
        self.canvas.bind("<Configure>", self.on_resize)

        # Store coordinates for labels and lines
        self.male_coords = {}
        self.female_coords = {}

        # Draw initial static lists (men left, women right)
        self.draw_lists()

    def _gen_prefs(self, group, other_group):
        prefs = {}
        for person in group:
            others = other_group[:]
            random.shuffle(others)
            prefs[person] = others
        return prefs

    def draw_lists(self):
        """Draw the fixed columns of male and female names, store their coordinates."""
        self.canvas.delete("all")
        width = self.canvas.winfo_width()
        height = self.canvas.winfo_height()
        if width < 10:
            width = 800
        if height < 10:
            height = 600

        left_x = width * 0.25
        right_x = width * 0.75
        start_y = 50
        step = (height - 100) / (self.n - 1) if self.n > 1 else 50

        # Draw male names (left)
        for i, male in enumerate(self.males):
            y = start_y + i * step
            self.canvas.create_text(left_x, y, text=male, font=("Arial", 12, "bold"), anchor="e", fill="#2c3e50")
            self.male_coords[male] = (left_x - 10, y)  # anchor point for line end

        # Draw female names (right)
        for i, female in enumerate(self.females):
            y = start_y + i * step
            self.canvas.create_text(right_x, y, text=female, font=("Arial", 12, "bold"), anchor="w", fill="#8e44ad")
            self.female_coords[female] = (right_x + 10, y)

        self.step_y = step
        self.start_y = start_y

    def draw_connections(self):
        """Redraw all current engagements (female -> male) as lines."""
        # Remove previous lines (keep text labels)
        for item in self.canvas.find_withtag("connection"):
            self.canvas.delete(item)

        for female, male in self.engagements.items():
            if male in self.male_coords and female in self.female_coords:
                x1, y1 = self.male_coords[male]
                x2, y2 = self.female_coords[female]
                self.canvas.create_line(x1, y1, x2, y2, fill="#e74c3c", width=2, smooth=True, tags="connection")
                # Also display pair text in the middle? optional, but not needed

    def on_resize(self, event):
        """Redraw lists and connections when window is resized."""
        self.draw_lists()
        self.draw_connections()

    def place_bet(self):
        male = self.male_var.get()
        female = self.female_var.get()
        if not male or not female:
            messagebox.showwarning("No selection", "Please select both a male and a female.")
            return
        self.bet_pair = (male, female)
        self.bet_label.config(text=f"Bet: {male} ⟷ {female}", fg="green")
        self.bet_placed = True
        messagebox.showinfo("Bet placed", f"You bet that {male} and {female} will end up together!")

    def next_round(self):
        if self.finished:
            messagebox.showinfo("Finished", "Algorithm already completed. Restart the program to play again.")
            return

        # Perform one round of proposals
        self.engagements, self.next_proposal, self.free_males, events = gale_shapley_step(
            self.males, self.females, self.male_prefs, self.female_prefs,
            self.engagements, self.next_proposal, self.free_males
        )

        self.round += 1
        self.info_label.config(text=f"Round {self.round} completed")

        # Show events in a dedicated popup or in a status bar; we'll use a simple messagebox with scroll?
        # Instead, show first few events in info label and print to console.
        if events:
            short = "\n".join(events[:3])
            if len(events) > 3:
                short += "\n..."
            self.info_label.config(text=f"Round {self.round}: {short}")
        else:
            self.info_label.config(text=f"Round {self.round}: No proposals (algorithm finished?)")

        # Redraw connections
        self.draw_connections()

        # Check if algorithm finished (no free males left)
        if not self.free_males:
            self.finished = True
            self.next_btn.config(state=tk.DISABLED, text="Completed")
            messagebox.showinfo("Algorithm finished", "All men are matched stably!")
            self.show_bet_result()

    def show_bet_result(self):
        if not self.bet_placed:
            return
        male, female = self.bet_pair
        matched = self.engagements.get(female) == male
        if matched:
            messagebox.showinfo("🎉 Bet Result", f"YOU WIN!\n{male} and {female} are a pair.")
        else:
            messagebox.showinfo("😢 Bet Result", f"Sorry, {male} and {female} did NOT end up together.\nBetter luck next time!")

# ---------------------- Run the app ----------------------
if __name__ == "__main__":
    root = tk.Tk()
    app = GaleShapleyGame(root)
    root.mainloop()
