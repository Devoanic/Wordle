"""Evaluation metrics for Wordle solver."""
from typing import List, Dict
import numpy as np
from src.game.word_manager import WordManager
from src.game.game_engine import WordleGame


class Evaluator:
    """Evaluates solver performance."""
    
    def __init__(self, word_manager: WordManager):
        """
        Initialize evaluator.
        
        Args:
            word_manager: WordManager instance
        """
        self.word_manager = word_manager
        self.solutions = word_manager.solutions
    
    def evaluate_solver(
        self,
        solver_fn,
        num_games: int = 100,
        solutions: List[str] = None
    ) -> Dict:
        """
        Evaluate a solver function.
        
        Args:
            solver_fn: Function that takes (guesses, feedback) and returns next guess
            num_games: Number of games to play
            solutions: Solutions to test (random if None)
            
        Returns:
            Dictionary with evaluation metrics
        """
        if solutions is None:
            import random
            solutions = random.sample(self.solutions, min(num_games, len(self.solutions)))
        
        results = {
            'games_won': 0,
            'games_lost': 0,
            'guess_counts': [],
            'win_rate': 0.0,
            'avg_guesses': 0.0,
            'guess_distribution': {i: 0 for i in range(1, 7)}
        }
        
        for solution in solutions[:num_games]:
            game = WordleGame(solution, self.word_manager)
            
            guesses = []
            feedback_list = []
            
            for turn in range(6):
                # Get next guess from solver
                next_guess = solver_fn(guesses, feedback_list)
                
                if not next_guess:
                    break
                
                try:
                    result = game.make_guess(next_guess)
                    guesses.append(next_guess)
                    feedback_list.append(result.feedback)
                    
                    if result.is_solved:
                        results['games_won'] += 1
                        results['guess_counts'].append(turn + 1)
                        results['guess_distribution'][turn + 1] += 1
                        # Track the solved word
                        try:
                            from src.game.word_tracker import track_solved_word
                            track_solved_word(solution)
                        except:
                            pass  # Don't fail evaluation if tracking fails
                        break
                except Exception as e:
                    print(f"Error in game: {e}")
                    break
            else:
                # Game not solved
                results['games_lost'] += 1
                results['guess_counts'].append(7)  # Failed
        
        # Calculate metrics
        results['win_rate'] = results['games_won'] / len(solutions[:num_games])
        if results['guess_counts']:
            results['avg_guesses'] = np.mean(results['guess_counts'])
        
        return results
    
    def print_results(self, results: Dict) -> None:
        """Print evaluation results."""
        print("\n" + "="*50)
        print("EVALUATION RESULTS")
        print("="*50)
        print(f"Games Played: {results['games_won'] + results['games_lost']}")
        print(f"Games Won: {results['games_won']}")
        print(f"Games Lost: {results['games_lost']}")
        print(f"Win Rate: {results['win_rate']:.2%}")
        print(f"Average Guesses: {results['avg_guesses']:.2f}")
        print("\nGuess Distribution:")
        for i in range(1, 7):
            count = results['guess_distribution'].get(i, 0)
            pct = count / (results['games_won'] + results['games_lost']) * 100
            print(f"  {i} guess(es): {count} games ({pct:.1f}%)")
        print("="*50)




