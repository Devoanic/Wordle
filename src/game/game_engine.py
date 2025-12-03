"""Wordle game engine with feedback generation."""
from enum import IntEnum
from typing import List, Tuple, Optional
from dataclasses import dataclass


class Feedback(IntEnum):
    """Feedback type for each letter position."""
    GRAY = 0    # Letter not in word
    YELLOW = 1  # Letter in word, wrong position
    GREEN = 2   # Letter in word, correct position


@dataclass
class GuessResult:
    """Result of a guess with feedback."""
    guess: str
    feedback: List[Feedback]
    is_solved: bool
    
    def __str__(self) -> str:
        """Visual representation of feedback."""
        # Use ASCII-friendly characters for Windows compatibility
        colors = {Feedback.GRAY: '[X]', Feedback.YELLOW: '[Y]', Feedback.GREEN: '[G]'}
        return ''.join(colors[f] for f in self.feedback)


class WordleGame:
    """Wordle game engine."""
    
    def __init__(self, solution: str, word_manager=None):
        """
        Initialize a Wordle game.
        
        Args:
            solution: The target word to guess
            word_manager: WordManager instance for validation
        """
        self.solution = solution.lower().strip()
        self.word_length = len(self.solution)
        self.word_manager = word_manager
        self.guess_history: List[GuessResult] = []
        self.max_guesses = 6
        self.is_solved = False
        self.is_game_over = False
    
    def make_guess(self, guess: str) -> GuessResult:
        """
        Make a guess and get feedback.
        
        Args:
            guess: The word to guess
            
        Returns:
            GuessResult with feedback
            
        Raises:
            ValueError: If guess is invalid
        """
        guess = guess.lower().strip()
        
        # Validate guess
        if len(guess) != self.word_length:
            raise ValueError(f"Guess must be {self.word_length} letters long")
        
        if not guess.isalpha():
            raise ValueError("Guess must contain only letters")
        
        if self.word_manager and not self.word_manager.is_valid_word(guess):
            raise ValueError(f"'{guess}' is not a valid word")
        
        # Check if game is over
        if self.is_game_over:
            raise ValueError("Game is already over")
        
        # Generate feedback
        feedback = self._generate_feedback(guess)
        is_solved = all(f == Feedback.GREEN for f in feedback)
        
        result = GuessResult(guess=guess, feedback=feedback, is_solved=is_solved)
        self.guess_history.append(result)
        
        if is_solved:
            self.is_solved = True
            self.is_game_over = True
        elif len(self.guess_history) >= self.max_guesses:
            self.is_game_over = True
        
        return result
    
    def _generate_feedback(self, guess: str) -> List[Feedback]:
        """
        Generate feedback for a guess.
        
        Algorithm:
        1. Mark GREEN positions first
        2. Count remaining letters in solution
        3. Mark YELLOW for letters in wrong position
        4. Mark GRAY for letters not in word
        """
        feedback = [Feedback.GRAY] * self.word_length
        solution_chars = list(self.solution)
        guess_chars = list(guess)
        
        # First pass: mark GREEN (exact matches)
        for i in range(self.word_length):
            if guess_chars[i] == solution_chars[i]:
                feedback[i] = Feedback.GREEN
                solution_chars[i] = None  # Mark as used
                guess_chars[i] = None     # Mark as processed
        
        # Second pass: mark YELLOW (letter in word, wrong position)
        for i in range(self.word_length):
            if guess_chars[i] is not None:  # Not already processed
                if guess_chars[i] in solution_chars:
                    feedback[i] = Feedback.YELLOW
                    # Remove first occurrence from solution
                    solution_chars[solution_chars.index(guess_chars[i])] = None
        
        return feedback
    
    def get_feedback_numeric(self) -> List[List[int]]:
        """Get feedback as numeric values (for ML model input)."""
        return [[int(f.value) for f in result.feedback] 
                for result in self.guess_history]
    
    def get_guess_history(self) -> List[str]:
        """Get list of all guesses made so far."""
        return [result.guess for result in self.guess_history]
    
    def get_state(self) -> dict:
        """Get current game state."""
        return {
            'guess_count': len(self.guess_history),
            'is_solved': self.is_solved,
            'is_game_over': self.is_game_over,
            'guesses': self.get_guess_history(),
            'feedback': self.get_feedback_numeric()
        }

