"""Baseline solvers for comparison."""
import random
import os
from pathlib import Path
from typing import List, Optional, Set
from src.game.game_engine import Feedback
from src.game.candidate_pruner import CandidatePruner
from src.game.word_manager import WordManager
from src.game.letter_analyzer import LetterAnalyzer


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
        
        # Load common Wordle solutions for weighting
        self.common_words: Set[str] = set()
        self._load_common_words()
        
        # Initialize letter analyzer for frequency-based suggestions
        self.letter_analyzer = LetterAnalyzer()
    
    def _load_common_words(self) -> None:
        """Load common Wordle solution words for priority weighting."""
        common_file = Path(__file__).parent.parent.parent / 'word_lists' / 'common_wordle_solutions.txt'
        if common_file.exists():
            with open(common_file, 'r', encoding='utf-8') as f:
                for line in f:
                    word = line.strip().lower()
                    if len(word) == 5 and word.isalpha():
                        self.common_words.add(word)
    
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
        
        # Filter out already-guessed words
        guessed_set = {g.lower() for g in guesses}
        candidates = [w for w in candidates if w.lower() not in guessed_set]
        
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
        """Select word with most common letters, preferring common Wordle solutions."""
        # Use letter analyzer for better frequency scoring
        def score(word):
            # Base score from letter frequency analysis
            base_score = self.letter_analyzer.score_word(word, consider_position=True)
            
            # Add significant bonus if word is a common Wordle solution
            if word in self.common_words:
                base_score += 1000  # Large bonus to prioritize common words
            
            # Also consider letter frequency in remaining candidates
            letter_freq = {}
            for cand in candidates:
                for letter in set(cand):
                    letter_freq[letter] = letter_freq.get(letter, 0) + 1
            base_score += sum(letter_freq.get(letter, 0) for letter in set(word))
            
            return base_score
        
        scored = [(score(word), word) for word in candidates]
        scored.sort(reverse=True)
        return scored[0][1] if scored else random.choice(candidates)
    
    def _entropy_based(self, candidates: List[str]) -> str:
        """Select word that maximizes expected information gain, preferring common Wordle solutions."""
        # First, check if any common Wordle words are in candidates
        common_candidates = [w for w in candidates if w in self.common_words]
        if common_candidates:
            # Prefer common words, but still score them
            candidates_to_check = common_candidates[:50] + [w for w in candidates if w not in self.common_words][:50]
        else:
            candidates_to_check = candidates[:100]
        
        # Enhanced entropy: use letter frequency analysis
        best_word = None
        best_score = -1
        
        # Calculate letter frequency in all candidates
        letter_freq = {}
        for cand in candidates:
            for letter in set(cand):
                letter_freq[letter] = letter_freq.get(letter, 0) + 1
        
        for word in candidates_to_check:
            # Base score from letter frequency analysis
            score = self.letter_analyzer.score_word(word, consider_position=True)
            
            # Count unique letters (entropy bonus)
            unique_letters = len(set(word))
            score += unique_letters * 10
            
            # Bonus for common letters in remaining candidates
            score += sum(letter_freq.get(letter, 0) for letter in set(word))
            
            # Large bonus if word is a common Wordle solution
            if word in self.common_words:
                score += 1000
            
            if score > best_score:
                best_score = score
                best_word = word
        
        return best_word if best_word else random.choice(candidates)




