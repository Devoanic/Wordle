"""Word list management for Wordle game."""
import os
from typing import List, Set
from pathlib import Path


class WordManager:
    """Manages word lists for solutions and allowed guesses."""
    
    def __init__(self, solutions_path: str = None, guesses_path: str = None):
        """
        Initialize word manager.
        
        Args:
            solutions_path: Path to solution words file (one per line)
            guesses_path: Path to allowed guesses file (one per line)
        """
        self.solutions: List[str] = []
        self.allowed_guesses: Set[str] = set()
        self.word_length = 5
        
        # Try to load from default location if no path provided
        if solutions_path is None:
            default_solutions = Path(__file__).parent.parent.parent / 'word_lists' / 'solutions.txt'
            if default_solutions.exists():
                solutions_path = str(default_solutions)
        
        if guesses_path is None:
            default_guesses = Path(__file__).parent.parent.parent / 'word_lists' / 'guesses.txt'
            if default_guesses.exists():
                guesses_path = str(default_guesses)
        
        if solutions_path and os.path.exists(solutions_path):
            self.load_solutions(solutions_path)
        elif not self.solutions:
            # Fall back to default word list if no file found
            self.generate_default_word_list()
        
        if guesses_path and os.path.exists(guesses_path):
            self.load_guesses(guesses_path)
        elif not self.allowed_guesses:
            # If no guesses file, use solutions as allowed guesses
            self.allowed_guesses = set(self.solutions)
    
    def load_solutions(self, file_path: str) -> None:
        """Load solution words from file."""
        self.solutions = []
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                word = line.strip().lower()
                if len(word) == self.word_length and word.isalpha():
                    self.solutions.append(word)
        print(f"Loaded {len(self.solutions)} solution words")
    
    def load_guesses(self, file_path: str) -> None:
        """Load allowed guess words from file."""
        self.allowed_guesses = set()
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                word = line.strip().lower()
                if len(word) == self.word_length and word.isalpha():
                    self.allowed_guesses.add(word)
        print(f"Loaded {len(self.allowed_guesses)} allowed guess words")
    
    def is_valid_word(self, word: str) -> bool:
        """Check if word is valid (in allowed guesses or solutions)."""
        word = word.lower().strip()
        if len(word) != self.word_length or not word.isalpha():
            return False
        return word in self.allowed_guesses or word in self.solutions
    
    def get_all_valid_words(self) -> List[str]:
        """Get all valid words (solutions + allowed guesses)."""
        all_words = set(self.solutions)
        all_words.update(self.allowed_guesses)
        return sorted(list(all_words))
    
    def generate_default_word_list(self) -> None:
        """Generate a default word list if none provided (for testing)."""
        # Common 5-letter words for testing
        common_words = [
            'apple', 'beach', 'chair', 'dance', 'earth', 'flame', 'globe',
            'horse', 'image', 'jolly', 'knife', 'light', 'magic', 'night',
            'ocean', 'piano', 'queen', 'rider', 'smile', 'table', 'uncle',
            'vital', 'water', 'xerox', 'young', 'zebra', 'brand', 'crown',
            'dwarf', 'epoxy', 'fancy', 'ghost', 'human', 'input', 'joust',
            'karma', 'lunch', 'minor', 'nurse', 'opium', 'proud', 'quest',
            'rally', 'saint', 'tiger', 'ultra', 'viral', 'wheat', 'xenon',
            'yearn', 'zonal', 'happy'
        ]
        self.solutions = common_words
        self.allowed_guesses = set(common_words)
        # Add more common guesses
        additional_guesses = [
            'slate', 'crane', 'trash', 'blast', 'could', 'would', 'their',
            'there', 'these', 'those', 'about', 'other', 'which', 'their',
            'first', 'water', 'after', 'where', 'great', 'think', 'years'
        ]
        self.allowed_guesses.update(additional_guesses)
        print(f"Generated default word list: {len(self.solutions)} solutions, "
              f"{len(self.allowed_guesses)} total valid words")

