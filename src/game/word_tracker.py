"""Utility to track and update common Wordle solutions."""
from pathlib import Path
from typing import Set


def load_common_words() -> Set[str]:
    """Load common Wordle solution words."""
    common_file = Path(__file__).parent.parent.parent / 'word_lists' / 'common_wordle_solutions.txt'
    common_words = set()
    if common_file.exists():
        with open(common_file, 'r', encoding='utf-8') as f:
            for line in f:
                word = line.strip().lower()
                if len(word) == 5 and word.isalpha():
                    common_words.add(word)
    return common_words


def add_common_word(word: str) -> bool:
    """
    Add a word to the common Wordle solutions list if not already present.
    
    Args:
        word: The word to add (will be converted to uppercase)
        
    Returns:
        True if word was added, False if it already existed
    """
    word = word.strip().lower()
    if len(word) != 5 or not word.isalpha():
        return False
    
    common_file = Path(__file__).parent.parent.parent / 'word_lists' / 'common_wordle_solutions.txt'
    
    # Load existing words
    existing_words = load_common_words()
    
    # Check if word already exists
    if word in existing_words:
        return False
    
    # Add word to file (append in uppercase)
    with open(common_file, 'a', encoding='utf-8') as f:
        f.write(f'\n{word.upper()}')
    
    return True


def track_solved_word(word: str) -> None:
    """
    Track a successfully solved word by adding it to common solutions.
    This is called automatically when a word is solved.
    
    Args:
        word: The word that was solved
    """
    try:
        added = add_common_word(word)
        if added:
            print(f"✓ Added '{word.upper()}' to common Wordle solutions")
    except Exception as e:
        # Silently fail - don't interrupt gameplay
        pass


