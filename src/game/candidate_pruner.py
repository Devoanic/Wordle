"""Candidate word pruning based on feedback constraints."""
from typing import List, Set, Optional
from .game_engine import Feedback


class CandidatePruner:
    """Prunes candidate words based on feedback from previous guesses."""
    
    def __init__(self, all_words: List[str]):
        """
        Initialize candidate pruner.
        
        Args:
            all_words: List of all valid words to consider
        """
        self.all_words = [w.lower() for w in all_words]
        self.candidates = set(self.all_words)
    
    def reset(self) -> None:
        """Reset to all words."""
        self.candidates = set(self.all_words)
    
    def apply_feedback(self, guess: str, feedback: List[Feedback]) -> Set[str]:
        """
        Update candidate set based on feedback.
        
        Args:
            guess: The word that was guessed
            feedback: Feedback for each position
            
        Returns:
            Updated set of candidate words
        """
        guess = guess.lower()
        
        # Track letter counts and positions
        green_letters = {}  # {position: letter}
        yellow_letters = {}  # {position: letter}
        gray_letters = set()
        min_required_count = {}  # {letter: minimum count required}
        
        # Process feedback
        for i, fb in enumerate(feedback):
            letter = guess[i]
            
            if fb == Feedback.GREEN:
                green_letters[i] = letter
                min_required_count[letter] = min_required_count.get(letter, 0) + 1
            elif fb == Feedback.YELLOW:
                yellow_letters[i] = letter
                min_required_count[letter] = min_required_count.get(letter, 0) + 1
            elif fb == Feedback.GRAY:
                gray_letters.add(letter)
        
        # Count total occurrences of each letter in guess
        guess_letter_counts = {}
        for letter in guess:
            guess_letter_counts[letter] = guess_letter_counts.get(letter, 0) + 1
        
        # Remove words that don't satisfy constraints
        valid_candidates = set()
        
        for word in self.candidates:
            if self._word_satisfies_constraints(
                word, green_letters, yellow_letters, gray_letters,
                min_required_count, guess_letter_counts
            ):
                valid_candidates.add(word)
        
        self.candidates = valid_candidates
        return self.candidates
    
    def _word_satisfies_constraints(
        self,
        word: str,
        green_letters: dict,
        yellow_letters: dict,
        gray_letters: set,
        min_required_count: dict,
        guess_letter_counts: dict
    ) -> bool:
        """
        Check if a word satisfies all feedback constraints.
        
        Returns:
            True if word could be the solution given the feedback
        """
        # Check GREEN constraints (exact position matches)
        for pos, letter in green_letters.items():
            if word[pos] != letter:
                return False
        
        # Check YELLOW constraints (letter in word but not at this position)
        for pos, letter in yellow_letters.items():
            if word[pos] == letter:  # Can't be in same position
                return False
            if letter not in word:  # Must be in word somewhere
                return False
        
        # Check GRAY constraints (letter not in word)
        # But be careful: if a letter appears as both gray and yellow/green,
        # it means the gray occurrences exceed the required count
        word_letter_counts = {}
        for letter in word:
            word_letter_counts[letter] = word_letter_counts.get(letter, 0) + 1
        
        for letter in gray_letters:
            # If letter was required (yellow/green), check exact count
            if letter in min_required_count:
                required = min_required_count[letter]
                if word_letter_counts.get(letter, 0) != required:
                    return False
            else:
                # Letter not required, should not be in word
                if letter in word:
                    return False
        
        # Check minimum required counts for yellow/green letters
        for letter, min_count in min_required_count.items():
            if word_letter_counts.get(letter, 0) < min_count:
                return False
        
        # Additional check: if a letter appears multiple times in guess,
        # ensure word has correct count
        for letter, guess_count in guess_letter_counts.items():
            word_count = word_letter_counts.get(letter, 0)
            # Count green + yellow for this letter
            required_count = sum(
                1 for pos in green_letters.values() if pos == letter
            ) + sum(
                1 for pos in yellow_letters.values() if pos == letter
            )
            
            if letter in gray_letters:
                # All occurrences beyond required must be gray
                if word_count > required_count:
                    return False
            else:
                # Must have at least required count
                if word_count < required_count:
                    return False
        
        return True
    
    def get_candidates(self) -> List[str]:
        """Get current list of candidate words."""
        return sorted(list(self.candidates))
    
    def get_candidate_count(self) -> int:
        """Get number of remaining candidates."""
        return len(self.candidates)

