"""Letter frequency and pattern analysis for Wordle."""
from pathlib import Path
from typing import Dict, List, Tuple
from collections import Counter


class LetterAnalyzer:
    """Analyzes letter frequency and patterns in Wordle solutions."""
    
    def __init__(self):
        """Initialize letter analyzer."""
        self.letter_freq: Dict[str, int] = {}
        self.position_freq: Dict[int, Dict[str, int]] = {i: {} for i in range(5)}
        self.vowels = set('aeiou')
        self.common_words = self._load_common_words()
        self._analyze_letters()
    
    def refresh(self) -> None:
        """Reload common words and re-analyze letter frequencies."""
        self.common_words = self._load_common_words()
        self._analyze_letters()
    
    def _load_common_words(self) -> List[str]:
        """Load common Wordle solution words."""
        common_file = Path(__file__).parent.parent.parent / 'word_lists' / 'common_wordle_solutions.txt'
        words = []
        if common_file.exists():
            with open(common_file, 'r', encoding='utf-8') as f:
                for line in f:
                    word = line.strip().lower()
                    if len(word) == 5 and word.isalpha():
                        words.append(word)
        return words
    
    def _analyze_letters(self) -> None:
        """Analyze letter frequency across all common solutions."""
        # Count letter frequency (overall)
        letter_counter = Counter()
        position_counters = {i: Counter() for i in range(5)}
        
        for word in self.common_words:
            for i, letter in enumerate(word):
                letter_counter[letter] += 1
                position_counters[i][letter] += 1
        
        self.letter_freq = dict(letter_counter)
        
        # Convert position counters to dicts
        for i in range(5):
            self.position_freq[i] = dict(position_counters[i])
    
    def get_letter_frequency(self, letter: str) -> int:
        """Get frequency of a letter across all solutions."""
        return self.letter_freq.get(letter.lower(), 0)
    
    def get_position_frequency(self, position: int, letter: str) -> int:
        """Get frequency of a letter at a specific position."""
        if 0 <= position < 5:
            return self.position_freq[position].get(letter.lower(), 0)
        return 0
    
    def get_vowel_count(self, word: str) -> int:
        """Count number of vowels in a word."""
        return sum(1 for letter in word.lower() if letter in self.vowels)
    
    def score_word(self, word: str, consider_position: bool = True) -> float:
        """
        Score a word based on letter frequency.
        
        Args:
            word: Word to score
            consider_position: Whether to consider position-specific frequency
            
        Returns:
            Score (higher is better)
        """
        word = word.lower()
        score = 0.0
        
        # Overall letter frequency
        unique_letters = set(word)
        for letter in unique_letters:
            score += self.get_letter_frequency(letter)
        
        # Position-specific frequency bonus
        if consider_position:
            for i, letter in enumerate(word):
                score += self.get_position_frequency(i, letter) * 0.5
        
        # Vowel bonus (words with 2-3 vowels are often good starting words)
        vowel_count = self.get_vowel_count(word)
        if vowel_count == 2 or vowel_count == 3:
            score += 100
        
        # Bonus for unique letters (no duplicates)
        if len(unique_letters) == 5:
            score += 50
        
        return score
    
    def get_best_starting_words(self, word_list: List[str], top_k: int = 10) -> List[Tuple[str, float]]:
        """
        Get best starting words based on letter frequency analysis.
        
        Args:
            word_list: List of words to evaluate
            top_k: Number of top words to return
            
        Returns:
            List of (word, score) tuples, sorted by score
        """
        scored_words = []
        for word in word_list:
            if len(word) == 5 and word.isalpha():
                score = self.score_word(word, consider_position=True)
                scored_words.append((word, score))
        
        scored_words.sort(key=lambda x: x[1], reverse=True)
        return scored_words[:top_k]
    
    def get_letter_stats(self) -> Dict[str, Dict]:
        """Get comprehensive letter statistics."""
        total_words = len(self.common_words)
        if total_words == 0:
            return {}
        
        stats = {}
        for letter in 'abcdefghijklmnopqrstuvwxyz':
            freq = self.get_letter_frequency(letter)
            position_freqs = [self.get_position_frequency(i, letter) for i in range(5)]
            most_common_pos = max(range(5), key=lambda i: position_freqs[i]) if position_freqs else -1
            
            stats[letter] = {
                'frequency': freq,
                'percentage': (freq / (total_words * 5)) * 100 if total_words > 0 else 0,
                'position_frequencies': position_freqs,
                'most_common_position': most_common_pos,
                'is_vowel': letter in self.vowels
            }
        
        return stats

