"""Baseline solvers for comparison."""
import random
from typing import List, Optional
from src.game.game_engine import Feedback
from src.game.candidate_pruner import CandidatePruner
from src.game.word_manager import WordManager


class BaselineSolver:
    """Baseline solvers using heuristics."""
    
    def __init__(self, word_manager: WordManager, strategy: str = 'random'):
        """
        Initialize baseline solver.
        
        Args:
            word_manager: WordManager instance
            strategy: 'random', 'entropy', or 'frequency'
        """
        self.word_manager = word_manager
        self.strategy = strategy
        self.all_words = word_manager.get_all_valid_words()
        self.pruner = CandidatePruner(self.all_words)
    
    def solve(
        self,
        guesses: List[str],
        feedback_list: List[List[Feedback]]
    ) -> Optional[str]:
        """
        Get next guess using baseline strategy.
        
        Args:
            guesses: Previous guesses
            feedback_list: Feedback for each guess
            
        Returns:
            Next guess word or None
        """
        # Reset and apply all feedback
        self.pruner.reset()
        for guess, feedback in zip(guesses, feedback_list):
            self.pruner.apply_feedback(guess, feedback)
        
        candidates = self.pruner.get_candidates()
        
        if not candidates:
            return None
        
        if self.strategy == 'random':
            return random.choice(candidates)
        elif self.strategy == 'frequency':
            return self._frequency_based(candidates)
        elif self.strategy == 'entropy':
            return self._entropy_based(candidates)
        else:
            return random.choice(candidates)
    
    def _frequency_based(self, candidates: List[str]) -> str:
        """Select word with most common letters."""
        # Calculate letter frequency in candidates
        letter_freq = {}
        for word in candidates:
            for letter in set(word):
                letter_freq[letter] = letter_freq.get(letter, 0) + 1
        
        # Score by unique letter frequency
        def score(word):
            return sum(letter_freq.get(letter, 0) for letter in set(word))
        
        scored = [(score(word), word) for word in candidates]
        scored.sort(reverse=True)
        return scored[0][1] if scored else random.choice(candidates)
    
    def _entropy_based(self, candidates: List[str]) -> str:
        """Select word that maximizes expected information gain."""
        # Simple entropy: prefer words with diverse letters
        best_word = None
        best_score = -1
        
        for word in candidates[:100]:  # Limit search for speed
            # Count unique letters and positions
            unique_letters = len(set(word))
            score = unique_letters * 10
            
            # Bonus for common letters in remaining candidates
            letter_freq = {}
            for cand in candidates:
                for letter in set(cand):
                    letter_freq[letter] = letter_freq.get(letter, 0) + 1
            
            score += sum(letter_freq.get(letter, 0) for letter in set(word))
            
            if score > best_score:
                best_score = score
                best_word = word
        
        return best_word if best_word else random.choice(candidates)


