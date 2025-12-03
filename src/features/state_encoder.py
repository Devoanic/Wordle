"""State encoding for game history."""
import numpy as np
from typing import List, Optional, Tuple
from .word_encoder import WordEncoder
from ..game.game_engine import Feedback


class StateEncoder:
    """Encodes game state (guesses + feedback) for ML models."""
    
    def __init__(self, word_length: int = 5, max_guesses: int = 6):
        """
        Initialize state encoder.
        
        Args:
            word_length: Length of words
            max_guesses: Maximum number of guesses
        """
        self.word_length = word_length
        self.max_guesses = max_guesses
        self.word_encoder = WordEncoder(word_length)
        self.alphabet_size = 26
    
    def encode_guess(self, guess: str) -> np.ndarray:
        """Encode a single guess as one-hot."""
        return self.word_encoder.one_hot_encode_flattened(guess)
    
    def encode_feedback(self, feedback: List[Feedback]) -> np.ndarray:
        """
        Encode feedback as numeric vector.
        
        Args:
            feedback: List of Feedback enums
            
        Returns:
            Array of shape (word_length,) with values 0, 1, or 2
        """
        return np.array([int(f.value) for f in feedback], dtype=np.float32)
    
    def encode_state(
        self,
        guesses: List[str],
        feedback_list: List[List[Feedback]],
        pad: bool = True
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        Encode complete game state.
        
        Args:
            guesses: List of previous guesses
            feedback_list: List of feedback for each guess
            pad: Whether to pad to max_guesses
            
        Returns:
            Tuple of (encoded_guesses, encoded_feedback)
            Shapes: ((num_guesses, word_length * alphabet_size), (num_guesses, word_length))
        """
        num_guesses = len(guesses)
        guess_dim = self.word_length * self.alphabet_size
        
        # Encode guesses
        if num_guesses == 0:
            # Handle empty case - create arrays with correct shape
            encoded_guesses = np.zeros((0, guess_dim), dtype=np.float32)
            encoded_feedback = np.zeros((0, self.word_length), dtype=np.float32)
        else:
            encoded_guesses = np.array([
                self.encode_guess(guess) for guess in guesses
            ])
            
            # Encode feedback
            encoded_feedback = np.array([
                self.encode_feedback(fb) for fb in feedback_list
            ])
        
        # Pad if requested
        if pad and num_guesses < self.max_guesses:
            padding_guesses = np.zeros((self.max_guesses - num_guesses, guess_dim))
            padding_feedback = np.zeros((self.max_guesses - num_guesses, self.word_length))
            
            encoded_guesses = np.vstack([encoded_guesses, padding_guesses])
            encoded_feedback = np.vstack([encoded_feedback, padding_feedback])
        
        return encoded_guesses, encoded_feedback
    
    def encode_state_concatenated(
        self,
        guesses: List[str],
        feedback_list: List[List[Feedback]]
    ) -> np.ndarray:
        """
        Encode state as single concatenated vector.
        
        Args:
            guesses: List of previous guesses
            feedback_list: List of feedback for each guess
            
        Returns:
            Flattened array with all guesses and feedback concatenated
        """
        encoded_guesses, encoded_feedback = self.encode_state(guesses, feedback_list, pad=True)
        
        # Concatenate guess and feedback for each turn
        turn_encodings = []
        for i in range(self.max_guesses):
            turn_vec = np.concatenate([encoded_guesses[i], encoded_feedback[i]])
            turn_encodings.append(turn_vec)
        
        return np.concatenate(turn_encodings)
    
    def encode_state_sequence(
        self,
        guesses: List[str],
        feedback_list: List[List[Feedback]]
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        Encode state as sequence (for LSTM/RNN models).
        
        Args:
            guesses: List of previous guesses
            feedback_list: List of feedback for each guess
            
        Returns:
            Tuple of (sequence_data, sequence_length)
            sequence_data: (max_guesses, word_length * alphabet_size + word_length)
            sequence_length: scalar (actual number of turns)
        """
        num_guesses = len(guesses)
        encoded_guesses, encoded_feedback = self.encode_state(guesses, feedback_list, pad=True)
        
        # Concatenate guess + feedback for each turn
        sequence = []
        for i in range(self.max_guesses):
            turn_vec = np.concatenate([encoded_guesses[i], encoded_feedback[i]])
            sequence.append(turn_vec)
        
        sequence_array = np.array(sequence)
        return sequence_array, num_guesses

