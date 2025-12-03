"""Data generation for training Wordle solver."""
import random
from typing import List, Tuple, Dict
import numpy as np
from src.game.word_manager import WordManager
from src.game.game_engine import WordleGame, Feedback
from src.game.candidate_pruner import CandidatePruner
from src.features.state_encoder import StateEncoder


class DataGenerator:
    """Generates training data by simulating Wordle games."""
    
    def __init__(
        self,
        word_manager: WordManager,
        state_encoder: StateEncoder,
        strategy: str = 'random'
    ):
        """
        Initialize data generator.
        
        Args:
            word_manager: WordManager instance
            state_encoder: StateEncoder instance
            strategy: 'random' or 'heuristic' for generating guesses
        """
        self.word_manager = word_manager
        self.state_encoder = state_encoder
        self.strategy = strategy
        self.all_words = word_manager.get_all_valid_words()
    
    def generate_game_data(
        self,
        solution: str = None,
        max_turns: int = 6
    ) -> List[Dict]:
        """
        Generate data from a single game.
        
        Args:
            solution: Target word (random if None)
            max_turns: Maximum number of turns to simulate
            
        Returns:
            List of training samples: [
                {
                    'state': encoded_state,
                    'next_guess': next_guess_word,
                    'solution': solution_word,
                    'turn': turn_number
                },
                ...
            ]
        """
        if solution is None:
            solution = random.choice(self.word_manager.solutions)
        
        game = WordleGame(solution, self.word_manager)
        pruner = CandidatePruner(self.all_words)
        
        training_samples = []
        
        for turn in range(max_turns):
            # Get current candidates
            candidates = pruner.get_candidates()
            
            if not candidates:
                break
            
            # Select next guess
            if self.strategy == 'random':
                next_guess = random.choice(candidates)
            elif self.strategy == 'heuristic':
                next_guess = self._heuristic_guess(candidates)
            else:
                next_guess = random.choice(candidates)
            
            # Make guess
            result = game.make_guess(next_guess)
            
            # Create training sample (state -> next guess)
            if len(game.guess_history) > 0:
                guesses = game.get_guess_history()
                feedback_list = [r.feedback for r in game.guess_history]
                
                # Encode state up to this point
                state_vec = self.state_encoder.encode_state_concatenated(
                    guesses[:-1], feedback_list[:-1]
                )
                
                # Target: index of the actual next guess word
                try:
                    next_guess_idx = self.all_words.index(next_guess)
                except ValueError:
                    continue  # Skip if word not in vocabulary
                
                sample = {
                    'state': state_vec,
                    'next_guess': next_guess,
                    'next_guess_idx': next_guess_idx,
                    'solution': solution,
                    'turn': turn + 1,
                    'feedback': result.feedback
                }
                
                training_samples.append(sample)
            
            # Update pruner
            pruner.apply_feedback(next_guess, result.feedback)
            
            # Check if solved
            if result.is_solved:
                break
        
        return training_samples
    
    def generate_dataset(
        self,
        num_games: int,
        solutions: List[str] = None
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        Generate training dataset.
        
        Args:
            num_games: Number of games to simulate
            solutions: List of solutions to use (random if None)
            
        Returns:
            Tuple of (states, targets)
            states: (num_samples, state_dim)
            targets: (num_samples,)
        """
        all_states = []
        all_targets = []
        
        for i in range(num_games):
            solution = random.choice(solutions) if solutions else None
            samples = self.generate_game_data(solution=solution)
            
            for sample in samples:
                all_states.append(sample['state'])
                all_targets.append(sample['next_guess_idx'])
        
        return np.array(all_states), np.array(all_targets)
    
    def _heuristic_guess(self, candidates: List[str]) -> str:
        """
        Select guess using heuristic (e.g., entropy-based).
        
        Simple version: pick word with most common letters.
        """
        if not candidates:
            return random.choice(self.all_words)
        
        # Simple heuristic: prefer words with common letters
        letter_freq = {}
        for word in candidates:
            for letter in set(word):
                letter_freq[letter] = letter_freq.get(letter, 0) + 1
        
        # Score words by unique letter frequency
        def score_word(word):
            return sum(letter_freq.get(letter, 0) for letter in set(word))
        
        scored = [(score_word(word), word) for word in candidates]
        scored.sort(reverse=True)
        
        return scored[0][1] if scored else random.choice(candidates)


