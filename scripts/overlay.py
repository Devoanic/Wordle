"""Wordle Overlay - Real-time solver assistant for Wordle game."""
import tkinter as tk
from tkinter import ttk, messagebox
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.game.word_manager import WordManager
from src.game.game_engine import Feedback
from src.evaluation.baseline import BaselineSolver
from scripts.solve import WordleSolver
from src.game.word_tracker import track_solved_word
from src.game.letter_analyzer import LetterAnalyzer


class WordleOverlay:
    """Overlay window for Wordle solver assistance."""
    
    def __init__(self, model_path=None, model_type='mlp', strategy='entropy'):
        self.root = tk.Tk()
        self.root.title("Wordle Solver Overlay")
        self.root.geometry("400x600")
        self.root.configure(bg='#121213')
        
        # Make window stay on top
        self.root.attributes('-topmost', True)
        self.root.attributes('-alpha', 0.95)  # Slight transparency
        
        # Initialize solver
        self.model_path = model_path
        self.model_type = model_type
        self.strategy = strategy
        self.solver = None
        self.baseline_solver = None
        
        # Game state
        self.guesses = []
        self.feedback_list = []
        
        # Initialize word manager
        self.word_manager = WordManager()
        if not self.word_manager.solutions:
            self.word_manager.generate_default_word_list()
        
        # Initialize letter analyzer
        self.letter_analyzer = LetterAnalyzer()
        
        # Initialize solver
        if model_path:
            try:
                self.solver = WordleSolver(model_path, model_type)
                self.solver_type = "ML"
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load ML model: {e}\nUsing baseline solver instead.")
                self.solver = None
        
        if not self.solver:
            self.baseline_solver = BaselineSolver(self.word_manager, strategy=strategy)
            self.solver_type = f"Baseline ({strategy})"
        
        self.setup_ui()
        self.update_suggestions()
    
    def setup_ui(self):
        """Set up the user interface."""
        # Header
        header_frame = tk.Frame(self.root, bg='#121213', pady=10)
        header_frame.pack(fill=tk.X)
        
        title_label = tk.Label(
            header_frame,
            text="Wordle Solver",
            font=('Arial', 18, 'bold'),
            bg='#121213',
            fg='#6AAA64'
        )
        title_label.pack()
        
        solver_label = tk.Label(
            header_frame,
            text=f"Mode: {self.solver_type}",
            font=('Arial', 10),
            bg='#121213',
            fg='#787C7E'
        )
        solver_label.pack()
        
        # Separator
        separator = tk.Frame(self.root, bg='#3A3A3C', height=1)
        separator.pack(fill=tk.X, padx=10, pady=5)
        
        # Current turn display
        turn_frame = tk.Frame(self.root, bg='#121213', pady=5)
        turn_frame.pack(fill=tk.X, padx=10)
        
        self.turn_label = tk.Label(
            turn_frame,
            text=f"Turn: {len(self.guesses) + 1}/6",
            font=('Arial', 12, 'bold'),
            bg='#121213',
            fg='#FFFFFF'
        )
        self.turn_label.pack()
        
        # Input section
        input_frame = tk.Frame(self.root, bg='#121213', pady=10)
        input_frame.pack(fill=tk.X, padx=10)
        
        # Guess input
        guess_label = tk.Label(
            input_frame,
            text="Your Guess:",
            font=('Arial', 10),
            bg='#121213',
            fg='#FFFFFF'
        )
        guess_label.pack(anchor=tk.W)
        
        guess_entry_frame = tk.Frame(input_frame, bg='#121213')
        guess_entry_frame.pack(fill=tk.X, pady=5)
        
        self.guess_entry = tk.Entry(
            guess_entry_frame,
            font=('Arial', 14, 'bold'),
            width=10,
            justify=tk.CENTER,
            bg='#3A3A3C',
            fg='#FFFFFF',
            insertbackground='#FFFFFF'
        )
        self.guess_entry.pack(side=tk.LEFT, padx=5)
        self.guess_entry.bind('<Return>', lambda e: self.add_guess())
        self.guess_entry.bind('<KeyRelease>', self.on_guess_change)
        
        # Feedback input
        feedback_label = tk.Label(
            input_frame,
            text="Feedback (G=Green, Y=Yellow, X=Gray):",
            font=('Arial', 10),
            bg='#121213',
            fg='#FFFFFF'
        )
        feedback_label.pack(anchor=tk.W, pady=(10, 5))
        
        feedback_entry_frame = tk.Frame(input_frame, bg='#121213')
        feedback_entry_frame.pack(fill=tk.X, pady=5)
        
        self.feedback_entry = tk.Entry(
            feedback_entry_frame,
            font=('Arial', 14, 'bold'),
            width=10,
            justify=tk.CENTER,
            bg='#3A3A3C',
            fg='#FFFFFF',
            insertbackground='#FFFFFF'
        )
        self.feedback_entry.pack(side=tk.LEFT, padx=5)
        self.feedback_entry.bind('<Return>', lambda e: self.add_guess())
        self.feedback_entry.bind('<KeyRelease>', self.on_feedback_change)
        
        # Add button
        add_btn = tk.Button(
            input_frame,
            text="Add Guess",
            command=self.add_guess,
            font=('Arial', 10, 'bold'),
            bg='#6AAA64',
            fg='#FFFFFF',
            activebackground='#5A9A54',
            activeforeground='#FFFFFF',
            relief=tk.FLAT,
            padx=20,
            pady=5
        )
        add_btn.pack(pady=10)
        
        # Clear button
        clear_btn = tk.Button(
            input_frame,
            text="Clear All",
            command=self.clear_all,
            font=('Arial', 9),
            bg='#787C7E',
            fg='#FFFFFF',
            activebackground='#686C6E',
            activeforeground='#FFFFFF',
            relief=tk.FLAT,
            padx=15,
            pady=3
        )
        clear_btn.pack()
        
        # Separator
        separator2 = tk.Frame(self.root, bg='#3A3A3C', height=1)
        separator2.pack(fill=tk.X, padx=10, pady=10)
        
        # Suggestions section
        suggestions_label = tk.Label(
            self.root,
            text="Top Suggestions:",
            font=('Arial', 12, 'bold'),
            bg='#121213',
            fg='#FFFFFF'
        )
        suggestions_label.pack(anchor=tk.W, padx=10, pady=(5, 10))
        
        # Suggestions list
        suggestions_frame = tk.Frame(self.root, bg='#121213')
        suggestions_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        self.suggestions_text = tk.Text(
            suggestions_frame,
            font=('Arial', 14, 'bold'),
            bg='#1A1A1C',
            fg='#6AAA64',
            wrap=tk.WORD,
            relief=tk.FLAT,
            padx=10,
            pady=10,
            height=8
        )
        self.suggestions_text.pack(fill=tk.BOTH, expand=True)
        
        # History section (collapsible)
        self.history_expanded = False
        history_btn = tk.Button(
            self.root,
            text="▼ Show History",
            command=self.toggle_history,
            font=('Arial', 9),
            bg='#121213',
            fg='#787C7E',
            activebackground='#121213',
            activeforeground='#FFFFFF',
            relief=tk.FLAT,
            anchor=tk.W
        )
        history_btn.pack(fill=tk.X, padx=10, pady=5)
        
        self.history_frame = tk.Frame(self.root, bg='#121213')
        self.history_text = tk.Text(
            self.history_frame,
            font=('Arial', 10),
            bg='#1A1A1C',
            fg='#FFFFFF',
            wrap=tk.WORD,
            relief=tk.FLAT,
            padx=10,
            pady=5,
            height=4
        )
        self.history_text.pack(fill=tk.BOTH, expand=True)
    
    def on_guess_change(self, event):
        """Handle guess input changes."""
        guess = self.guess_entry.get().upper()[:5]
        self.guess_entry.delete(0, tk.END)
        self.guess_entry.insert(0, guess)
    
    def on_feedback_change(self, event):
        """Handle feedback input changes."""
        feedback = self.feedback_entry.get().upper()[:5]
        # Convert to standard format
        feedback = feedback.replace('2', 'G').replace('1', 'Y').replace('0', 'X')
        self.feedback_entry.delete(0, tk.END)
        self.feedback_entry.insert(0, feedback)
    
    def feedback_from_string(self, feedback_str: str):
        """Convert string feedback to Feedback enum list."""
        feedback_map = {
            'G': Feedback.GREEN,
            'Y': Feedback.YELLOW,
            'X': Feedback.GRAY,
            '2': Feedback.GREEN,
            '1': Feedback.YELLOW,
            '0': Feedback.GRAY
        }
        
        feedback = []
        for char in feedback_str.upper():
            if char in feedback_map:
                feedback.append(feedback_map[char])
            else:
                raise ValueError(f"Invalid feedback character: {char}")
        
        return feedback
    
    def add_guess(self):
        """Add a guess and feedback to the game state."""
        guess = self.guess_entry.get().strip().lower()
        feedback_str = self.feedback_entry.get().strip().upper()
        
        if len(guess) != 5:
            messagebox.showerror("Error", "Guess must be 5 letters!")
            return
        
        if len(feedback_str) != 5:
            messagebox.showerror("Error", "Feedback must be 5 characters (G/Y/X)!")
            return
        
        try:
            feedback = self.feedback_from_string(feedback_str)
        except ValueError as e:
            messagebox.showerror("Error", str(e))
            return
        
        # Add to history
        self.guesses.append(guess)
        self.feedback_list.append(feedback)
        
        # Clear inputs
        self.guess_entry.delete(0, tk.END)
        self.feedback_entry.delete(0, tk.END)
        
        # Update UI
        self.update_turn_label()
        self.update_history()
        self.update_suggestions()
        
        # Check if solved
        if all(f == Feedback.GREEN for f in feedback):
            messagebox.showinfo("Solved!", f"Congratulations! Solved in {len(self.guesses)} guesses!")
            # Track the solved word
            self._track_solved_word(guess)
            # Refresh letter analyzer to include new word in statistics
            self.letter_analyzer.refresh()
    
    def clear_all(self):
        """Clear all guesses and reset."""
        self.guesses = []
        self.feedback_list = []
        self.guess_entry.delete(0, tk.END)
        self.feedback_entry.delete(0, tk.END)
        self.update_turn_label()
        self.update_history()
        self.update_suggestions()
    
    def update_turn_label(self):
        """Update turn label."""
        turn = len(self.guesses) + 1
        if turn > 6:
            self.turn_label.config(text="Game Over", fg='#787C7E')
        else:
            self.turn_label.config(text=f"Turn: {turn}/6", fg='#FFFFFF')
    
    def update_history(self):
        """Update history display."""
        self.history_text.delete(1.0, tk.END)
        if not self.guesses:
            self.history_text.insert(tk.END, "No guesses yet...")
            return
        
        for i, (guess, feedback) in enumerate(zip(self.guesses, self.feedback_list), 1):
            feedback_str = ''.join(['G' if f == Feedback.GREEN else 'Y' if f == Feedback.YELLOW else 'X' 
                                   for f in feedback])
            self.history_text.insert(tk.END, f"Turn {i}: {guess.upper()} - {feedback_str}\n")
    
    def update_suggestions(self):
        """Update suggestions based on current game state."""
        self.suggestions_text.delete(1.0, tk.END)
        
        if not self.guesses:
            # Show optimal starting words for first guess
            all_words = self.word_manager.get_all_valid_words()
            best_starters = self.letter_analyzer.get_best_starting_words(all_words, top_k=5)
            
            self.suggestions_text.insert(tk.END, "Optimal Starting Words:\n\n")
            for i, (word, score) in enumerate(best_starters, 1):
                vowel_count = self.letter_analyzer.get_vowel_count(word)
                self.suggestions_text.insert(tk.END, f"{i}. {word.upper()} (Score: {score:.0f}, Vowels: {vowel_count})\n")
            
            self.suggestions_text.insert(tk.END, "\nTip: Words with 2-3 vowels and unique letters work best!")
            return
        
        try:
            if self.solver:
                # Use ML solver
                suggestions = self.get_ml_suggestions()
            else:
                # Use baseline solver
                suggestions = self.get_baseline_suggestions()
            
            if not suggestions:
                self.suggestions_text.insert(tk.END, "No valid candidates found!")
                return
            
            # Display top suggestions
            for i, word in enumerate(suggestions[:5], 1):
                self.suggestions_text.insert(tk.END, f"{i}. {word.upper()}\n")
                if i == 1:
                    # Highlight top suggestion
                    start = f"1.0 + {i-1} lines"
                    end = f"1.0 + {i} lines"
                    self.suggestions_text.tag_add("top", start, end)
                    self.suggestions_text.tag_config("top", foreground='#6AAA64', font=('Arial', 16, 'bold'))
        
        except Exception as e:
            self.suggestions_text.insert(tk.END, f"Error: {str(e)}")
    
    def get_ml_suggestions(self):
        """Get suggestions from ML model."""
        next_guess = self.solver.predict_next_guess(self.guesses, self.feedback_list)
        if not next_guess:
            return []
        
        # Get top candidates from pruner
        self.solver.pruner.reset()
        for guess, feedback in zip(self.guesses, self.feedback_list):
            self.solver.pruner.apply_feedback(guess, feedback)
        
        candidates = self.solver.pruner.get_candidates()
        
        # Put ML suggestion first
        suggestions = [next_guess] if next_guess else []
        for word in candidates:
            if word not in suggestions:
                suggestions.append(word)
        
        return suggestions[:10]
    
    def get_baseline_suggestions(self):
        """Get suggestions from baseline solver."""
        next_guess = self.baseline_solver.solve(self.guesses, self.feedback_list)
        if not next_guess:
            return []
        
        # Get all candidates
        self.baseline_solver.pruner.reset()
        for guess, feedback in zip(self.guesses, self.feedback_list):
            self.baseline_solver.pruner.apply_feedback(guess, feedback)
        
        candidates = self.baseline_solver.pruner.get_candidates()
        
        # Put solver suggestion first
        suggestions = [next_guess] if next_guess else []
        for word in candidates:
            if word not in suggestions:
                suggestions.append(word)
        
        return suggestions[:10]
    
    def toggle_history(self):
        """Toggle history display."""
        if self.history_expanded:
            self.history_frame.pack_forget()
            self.history_expanded = False
        else:
            self.history_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
            self.history_expanded = True
            self.update_history()
    
    def _track_solved_word(self, word: str):
        """Track a successfully solved word."""
        track_solved_word(word)
        # Refresh letter analyzer to update statistics
        self.letter_analyzer.refresh()
    
    def run(self):
        """Start the overlay."""
        self.root.mainloop()


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Wordle Solver Overlay')
    parser.add_argument('--model', type=str, default=None, help='Path to ML model')
    parser.add_argument('--model-type', type=str, default='mlp', choices=['mlp', 'lstm'],
                        help='Model architecture')
    parser.add_argument('--strategy', type=str, default='entropy',
                        choices=['random', 'frequency', 'entropy'],
                        help='Baseline strategy (if not using ML model)')
    
    args = parser.parse_args()
    
    if args.model:
        import os
        if not os.path.exists(args.model):
            print(f"Error: Model file not found: {args.model}")
            print("Starting with baseline solver instead...")
            args.model = None
    
    overlay = WordleOverlay(
        model_path=args.model,
        model_type=args.model_type,
        strategy=args.strategy
    )
    overlay.run()


if __name__ == '__main__':
    main()

