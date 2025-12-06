"""Evaluation script for Wordle solver."""
import argparse
import sys
import os
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import torch
from src.game.word_manager import WordManager
from src.evaluation.metrics import Evaluator
from src.evaluation.baseline import BaselineSolver
from scripts.solve import WordleSolver


def create_ml_solver_fn(model_path: str, model_type: str = 'mlp'):
    """Create a solver function from ML model."""
    solver = WordleSolver(model_path, model_type)
    
    def solve_fn(guesses, feedback_list):
        return solver.predict_next_guess(guesses, feedback_list)
    
    return solve_fn


def main():
    parser = argparse.ArgumentParser(description='Evaluate Wordle Solver')
    parser.add_argument('--model', type=str, default=None, help='Path to ML model')
    parser.add_argument('--model-type', type=str, default='mlp', choices=['mlp', 'lstm'],
                        help='Model architecture')
    parser.add_argument('--baseline', type=str, default=None,
                        choices=['random', 'frequency', 'entropy'],
                        help='Baseline strategy to compare')
    parser.add_argument('--num-games', type=int, default=100,
                        help='Number of games to evaluate')
    
    args = parser.parse_args()
    
    # Initialize word manager
    word_manager = WordManager()
    if not word_manager.solutions:
        word_manager.generate_default_word_list()
    
    evaluator = Evaluator(word_manager)
    
    # Evaluate ML model
    if args.model and os.path.exists(args.model):
        print(f"\nEvaluating ML model: {args.model}")
        ml_solver = create_ml_solver_fn(args.model, args.model_type)
        ml_results = evaluator.evaluate_solver(ml_solver, num_games=args.num_games)
        evaluator.print_results(ml_results)
    
    # Evaluate baseline
    if args.baseline:
        print(f"\nEvaluating baseline: {args.baseline}")
        baseline_solver = BaselineSolver(word_manager, strategy=args.baseline)
        baseline_results = evaluator.evaluate_solver(
            baseline_solver.solve, num_games=args.num_games
        )
        evaluator.print_results(baseline_results)
    
    if not args.model and not args.baseline:
        print("Error: Must specify --model or --baseline")
        sys.exit(1)


if __name__ == '__main__':
    main()





