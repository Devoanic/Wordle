"""Test solving a specific word with baseline or ML solver."""
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.game.word_manager import WordManager
from src.game.game_engine import WordleGame, Feedback
from src.evaluation.baseline import BaselineSolver
from scripts.solve import WordleSolver


def print_feedback_visual(feedback):
    """Print visual representation of feedback."""
    colors = {
        Feedback.GRAY: '[X]',
        Feedback.YELLOW: '[Y]',
        Feedback.GREEN: '[G]'
    }
    return ''.join(colors[f] for f in feedback)


def solve_word_baseline(word: str, strategy: str = 'entropy'):
    """Solve a word using baseline solver."""
    print(f"\n{'='*60}")
    print(f"Solving word: {word.upper()}")
    print(f"Strategy: {strategy}")
    print(f"{'='*60}\n")
    
    word_manager = WordManager()
    if not word_manager.solutions:
        word_manager.generate_default_word_list()
    
    # Add word to word list if not present (for testing)
    if word not in word_manager.solutions:
        word_manager.solutions.append(word)
        word_manager.allowed_guesses.add(word)
        print(f"Note: Added '{word}' to word list for testing\n")
    
    game = WordleGame(word, word_manager)
    solver = BaselineSolver(word_manager, strategy=strategy)
    
    guesses = []
    feedback_list = []
    
    for turn in range(6):
        # Get next guess
        next_guess = solver.solve(guesses, feedback_list)
        
        if not next_guess:
            print("No valid candidates!")
            break
        
        # Make guess
        result = game.make_guess(next_guess)
        guesses.append(next_guess)
        feedback_list.append(result.feedback)
        
        print(f"Turn {turn + 1}: {next_guess.upper():<10} {print_feedback_visual(result.feedback)}")
        
        if result.is_solved:
            print(f"\n✅ Solved in {turn + 1} guess(es)!")
            return turn + 1
    
    print(f"\n❌ Failed to solve in 6 guesses")
    print(f"Solution was: {word.upper()}")
    return 7


def solve_word_ml(word: str, model_path: str, model_type: str = 'mlp'):
    """Solve a word using ML model."""
    print(f"\n{'='*60}")
    print(f"Solving word: {word.upper()}")
    print(f"Model: {model_path}")
    print(f"{'='*60}\n")
    
    solver = WordleSolver(model_path, model_type)
    
    # Add word to word list if not present (for testing)
    if word not in solver.word_manager.solutions:
        solver.word_manager.solutions.append(word)
        solver.word_manager.allowed_guesses.add(word)
        # Update the solver's word list
        solver.all_words = solver.word_manager.get_all_valid_words()
        print(f"Note: Added '{word}' to word list for testing\n")
    
    game = WordleGame(word, solver.word_manager)
    
    guesses = []
    feedback_list = []
    
    for turn in range(6):
        # Get prediction
        next_guess = solver.predict_next_guess(guesses, feedback_list)
        
        if not next_guess:
            print("No valid candidates!")
            break
        
        # Make guess
        result = game.make_guess(next_guess)
        guesses.append(next_guess)
        feedback_list.append(result.feedback)
        
        print(f"Turn {turn + 1}: {next_guess.upper():<10} {print_feedback_visual(result.feedback)}")
        
        if result.is_solved:
            print(f"\n✅ Solved in {turn + 1} guess(es)!")
            return turn + 1
    
    print(f"\n❌ Failed to solve in 6 guesses")
    print(f"Solution was: {word.upper()}")
    return 7


def main():
    parser = argparse.ArgumentParser(description='Test solving a specific word')
    parser.add_argument('word', type=str, help='Word to solve (5 letters)')
    parser.add_argument('--model', type=str, default=None, help='Path to ML model (uses baseline if not provided)')
    parser.add_argument('--model-type', type=str, default='mlp', choices=['mlp', 'lstm'],
                        help='Model architecture (if using ML model)')
    parser.add_argument('--strategy', type=str, default='entropy',
                        choices=['random', 'frequency', 'entropy'],
                        help='Baseline strategy (if not using ML model)')
    
    args = parser.parse_args()
    
    word = args.word.lower().strip()
    
    if len(word) != 5:
        print(f"Error: Word must be 5 letters long, got '{word}' ({len(word)} letters)")
        sys.exit(1)
    
    if not word.isalpha():
        print(f"Error: Word must contain only letters, got '{word}'")
        sys.exit(1)
    
    if args.model:
        import os
        if not os.path.exists(args.model):
            print(f"Error: Model file not found: {args.model}")
            sys.exit(1)
        solve_word_ml(word, args.model, args.model_type)
    else:
        solve_word_baseline(word, args.strategy)


if __name__ == '__main__':
    main()

