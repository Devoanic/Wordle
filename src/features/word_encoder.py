"""Word encoding for ML models."""
import numpy as np
from typing import List, Union


class WordEncoder:
    """Encodes words into numerical features."""
    
    def __init__(self, word_length: int = 5):
        """
        Initialize word encoder.
        
        Args:
            word_length: Length of words to encode
        """
        self.word_length = word_length
        self.alphabet_size = 26
        self.char_to_idx = {chr(ord('a') + i): i for i in range(26)}
        self.idx_to_char = {i: chr(ord('a') + i) for i in range(26)}
    
    def one_hot_encode(self, word: str) -> np.ndarray:
        """
        Encode word as one-hot vectors per position.
        
        Args:
            word: Word to encode (lowercase)
            
        Returns:
            Array of shape (word_length, alphabet_size)
        """
        word = word.lower().strip()
        if len(word) != self.word_length:
            raise ValueError(f"Word must be {self.word_length} letters long")
        
        encoding = np.zeros((self.word_length, self.alphabet_size), dtype=np.float32)
        
        for i, char in enumerate(word):
            if char in self.char_to_idx:
                encoding[i, self.char_to_idx[char]] = 1.0
        
        return encoding
    
    def one_hot_encode_flattened(self, word: str) -> np.ndarray:
        """
        Encode word as flattened one-hot vector.
        
        Args:
            word: Word to encode
            
        Returns:
            Array of shape (word_length * alphabet_size,)
        """
        return self.one_hot_encode(word).flatten()
    
    def integer_encode(self, word: str) -> np.ndarray:
        """
        Encode word as integer indices.
        
        Args:
            word: Word to encode
            
        Returns:
            Array of shape (word_length,) with values 0-25
        """
        word = word.lower().strip()
        return np.array([self.char_to_idx.get(char, 0) for char in word], dtype=np.int64)
    
    def encode_batch(self, words: List[str], method: str = 'one_hot') -> np.ndarray:
        """
        Encode multiple words.
        
        Args:
            words: List of words to encode
            method: 'one_hot' or 'integer'
            
        Returns:
            Array of encoded words
        """
        if method == 'one_hot':
            return np.array([self.one_hot_encode_flattened(w) for w in words])
        elif method == 'integer':
            return np.array([self.integer_encode(w) for w in words])
        else:
            raise ValueError(f"Unknown encoding method: {method}")
    
    def decode(self, encoding: np.ndarray, method: str = 'integer') -> str:
        """
        Decode encoding back to word.
        
        Args:
            encoding: Encoded representation
            method: 'one_hot' or 'integer'
            
        Returns:
            Decoded word string
        """
        if method == 'integer':
            indices = encoding
        elif method == 'one_hot':
            # Reshape if flattened
            if encoding.ndim == 1:
                encoding = encoding.reshape(self.word_length, self.alphabet_size)
            indices = np.argmax(encoding, axis=1)
        else:
            raise ValueError(f"Unknown encoding method: {method}")
        
        return ''.join(self.idx_to_char.get(int(idx), '?') for idx in indices)


