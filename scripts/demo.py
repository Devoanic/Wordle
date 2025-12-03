"""Quick demo of Wordle game engine."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.game.word_manager import WordManager
from src.game.game_engine import WordleGame, Feedback


def demo_game():
    """Demo a simple Wordle game."""
    print("="*60)
    print("Wordle Game Engine Demo")
    print("="*60)
    
    # Initialize word manager
    word_manager = WordManager()
    word_manager.generate_default_word_list()
    
    # Create a game
    solution = "apple"
    print(f"\nSolution word: {solution.upper()}")
    print("\nLet's play Wordle!\n")
    
    game = WordleGame(solution, word_manager)
    
    guesses = ["crane", "slate", "apple"]
    
    for i, guess in enumerate(guesses, 1):
        try:
            result = game.make_guess(guess)
            print(f"Turn {i}: {guess.upper()}")
            print(f"Feedback: {result}")
            print()
            
            if result.is_solved:
                print("Solved!")
                break
        except ValueError as e:
            print(f"Error: {e}")
    
    print(f"\nGame state:")
    print(f"  Solved: {game.is_solved}")
    print(f"  Guesses made: {len(game.guess_history)}")
    print(f"  Game over: {game.is_game_over}")


def demo_feedback():
    """Demo feedback generation."""
    print("\n" + "="*60)
    print("Feedback Generation Demo")
    print("="*60)
    
    word_manager = WordManager()
    word_manager.generate_default_word_list()
    
    solution = "apple"
    game = WordleGame(solution, word_manager)
    
    test_guesses = [
        ("slate", "Testing single letter match"),
        ("crane", "Testing multiple letters"),
        ("apple", "Testing correct word")
    ]
    
    for guess, description in test_guesses:
        result = game.make_guess(guess)
        print(f"\n{description}")
        print(f"Solution: {solution.upper()}")
        print(f"Guess:    {guess.upper()}")
        print(f"Feedback: {result}")
        
        # Reset for next test
        game = WordleGame(solution, word_manager)


if __name__ == '__main__':
    demo_game()
    demo_feedback()

