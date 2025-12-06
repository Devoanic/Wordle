"""Interactive CLI for Wordle solver."""
import argparse
import sys
import os
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

import torch
from src.game.word_manager import WordManager
from src.game.game_engine import WordleGame, Feedback
from src.game.candidate_pruner import CandidatePruner
from src.features.state_encoder import StateEncoder
from src.models.mlp_model import MLPWordleSolver
from src.models.lstm_model import LSTMWordleSolver


class WordleSolver:
    """ML-based Wordle solver."""
    
    def __init__(self, model_path: str, model_type: str = 'mlp'):
        """
        Initialize solver.
        
        Args:
            model_path: Path to trained model
            model_type: 'mlp' or 'lstm'
        """
        self.word_manager = WordManager()
        if not self.word_manager.solutions:
            self.word_manager.generate_default_word_list()
        
        self.all_words = self.word_manager.get_all_valid_words()
        self.state_encoder = StateEncoder(word_length=5, max_guesses=6)
        self.pruner = CandidatePruner(self.all_words)
        
        # Load model
        self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
        self.model_type = model_type
        
        # Calculate dimensions
        guess_dim = 5 * 26
        feedback_dim = 5
        
        if model_type == 'mlp':
            input_dim = 6 * (guess_dim + feedback_dim)
            self.model = MLPWordleSolver(input_dim, len(self.all_words))
        else:
            input_dim = guess_dim + feedback_dim
            self.model = LSTMWordleSolver(input_dim, len(self.all_words))
        
        # Load weights
        checkpoint = torch.load(model_path, map_location=self.device)
        self.model.load_state_dict(checkpoint['model_state_dict'])
        self.model.to(self.device)
        self.model.eval()
    
    def predict_next_guess(
        self,
        guesses: list,
        feedback_list: list
    ) -> str:
        """
        Predict next guess.
        
        Args:
            guesses: List of previous guesses
            feedback_list: List of feedback for each guess
            
        Returns:
            Recommended next guess
        """
        # Prune candidates
        self.pruner.reset()
        for guess, feedback in zip(guesses, feedback_list):
            self.pruner.apply_feedback(guess, feedback)
        
        candidates = self.pruner.get_candidates()
        
        if not candidates:
            return None
        
        # Encode state
        if self.model_type == 'mlp':
            state_vec = self.state_encoder.encode_state_concatenated(
                guesses, feedback_list
            )
            state_tensor = torch.FloatTensor(state_vec).unsqueeze(0).to(self.device)
            
            with torch.no_grad():
                logits = self.model(state_tensor)
                probs = torch.softmax(logits, dim=-1)
                top_probs, top_indices = torch.topk(probs, k=min(10, len(self.all_words)))
        
        else:  # lstm
            sequence, length = self.state_encoder.encode_state_sequence(
                guesses, feedback_list
            )
            sequence_tensor = torch.FloatTensor(sequence).unsqueeze(0).to(self.device)
            length_tensor = torch.LongTensor([length]).to(self.device)
            
            with torch.no_grad():
                logits = self.model(sequence_tensor, length_tensor)
                probs = torch.softmax(logits, dim=-1)
                top_probs, top_indices = torch.topk(probs, k=min(10, len(self.all_words)))
        
        # Filter to valid candidates
        top_words = [self.all_words[idx] for idx in top_indices[0].cpu().numpy()]
        valid_predictions = [w for w in top_words if w in candidates]
        
        # Prefer common Wordle solutions if available
        if valid_predictions:
            common_words = self._load_common_words()
            common_predictions = [w for w in valid_predictions if w in common_words]
            if common_predictions:
                return common_predictions[0]
            return valid_predictions[0]
        
        # If no ML predictions, prefer common words from candidates
        if candidates:
            common_words = self._load_common_words()
            common_candidates = [w for w in candidates if w in common_words]
            if common_candidates:
                return common_candidates[0]
        
        return candidates[0] if candidates else None
    
    def _load_common_words(self):
        """Load common Wordle solution words."""
        from pathlib import Path
        common_file = Path(__file__).parent.parent / 'word_lists' / 'common_wordle_solutions.txt'
        common_words = set()
        if common_file.exists():
            with open(common_file, 'r', encoding='utf-8') as f:
                for line in f:
                    word = line.strip().lower()
                    if len(word) == 5 and word.isalpha():
                        common_words.add(word)
        return common_words


def feedback_from_string(feedback_str: str) -> list:
    """Convert string feedback to Feedback enum list."""
    feedback_map = {
        'g': Feedback.GREEN,
        'y': Feedback.YELLOW,
        'x': Feedback.GRAY,
        '0': Feedback.GRAY,
        '1': Feedback.YELLOW,
        '2': Feedback.GREEN
    }
    
    feedback = []
    for char in feedback_str.lower():
        if char in feedback_map:
            feedback.append(feedback_map[char])
        else:
            raise ValueError(f"Invalid feedback character: {char}")
    
    return feedback


def print_feedback_visual(feedback: list) -> None:
    """Print visual representation of feedback."""
    # Use ASCII-friendly characters for Windows compatibility
    colors = {
        Feedback.GRAY: '[X]',
        Feedback.YELLOW: '[Y]',
        Feedback.GREEN: '[G]'
    }
    print(''.join(colors[f] for f in feedback))


def interactive_mode(model_path: str, model_type: str = 'mlp'):
    """Run interactive solving mode."""
    solver = WordleSolver(model_path, model_type)
    
    print("\n" + "="*60)
    print("ML Wordle Solver - Interactive Mode")
    print("="*60)
    print("\nEnter your guesses and feedback.")
    print("Feedback format: g=green, y=yellow, x=gray (e.g., 'gyxxg')")
    print("Or use numbers: 2=green, 1=yellow, 0=gray")
    print("Type 'quit' to exit\n")
    
    guesses = []
    feedback_list = []
    
    for turn in range(6):
        if guesses:
            # Predict next guess
            try:
                next_guess = solver.predict_next_guess(guesses, feedback_list)
                print(f"\n🤖 Suggested guess: {next_guess.upper()}")
            except Exception as e:
                print(f"Error predicting: {e}")
                next_guess = None
        
        # Get user input
        guess = input(f"\nTurn {turn + 1}/6 - Enter your guess: ").strip().lower()
        
        if guess == 'quit':
            break
        
        if not guess or len(guess) != 5:
            print("Invalid guess. Please enter a 5-letter word.")
            continue
        
        feedback_str = input("Enter feedback (gyxxg or 21002): ").strip().lower()
        
        if len(feedback_str) != 5:
            print("Invalid feedback. Please enter 5 characters.")
            continue
        
        try:
            feedback = feedback_from_string(feedback_str)
            guesses.append(guess)
            feedback_list.append(feedback)
            
            print(f"\nGuess: {guess.upper()}")
            print("Feedback: ", end='')
            print_feedback_visual(feedback)
            
            # Check if solved
            if all(f == Feedback.GREEN for f in feedback):
                print("\n🎉 Congratulations! Word solved!")
                break
        
        except ValueError as e:
            print(f"Error: {e}")
            continue
    
    print("\nGame over!")


def solve_mode(model_path: str, solution: str, model_type: str = 'mlp'):
    """Solve a specific word automatically."""
    solver = WordleSolver(model_path, model_type)
    game = WordleGame(solution, solver.word_manager)
    
    guesses = []
    feedback_list = []
    
    print(f"\nSolving for: {solution.upper()}\n")
    
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
        
        print(f"Turn {turn + 1}: {next_guess.upper()} - ", end='')
        print_feedback_visual(result.feedback)
        
        if result.is_solved:
            print(f"\n✅ Solved in {turn + 1} guesses!")
            # Track the solved word
            from src.game.word_tracker import track_solved_word
            track_solved_word(solution)
            return turn + 1
    
    print(f"\n❌ Failed to solve in 6 guesses")
    return 7


def main():
    parser = argparse.ArgumentParser(description='Wordle Solver CLI')
    parser.add_argument('--model', type=str, required=True, help='Path to model file')
    parser.add_argument('--model-type', type=str, default='mlp', choices=['mlp', 'lstm'],
                        help='Model architecture')
    parser.add_argument('--solution', type=str, default=None,
                        help='Word to solve (for auto mode)')
    parser.add_argument('--interactive', action='store_true',
                        help='Run in interactive mode')
    
    args = parser.parse_args()
    
    if not os.path.exists(args.model):
        print(f"Error: Model file not found: {args.model}")
        sys.exit(1)
    
    if args.interactive or args.solution is None:
        interactive_mode(args.model, args.model_type)
    else:
        solve_mode(args.model, args.solution, args.model_type)


if __name__ == '__main__':
    main()

