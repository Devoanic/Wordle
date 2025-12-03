"""Multi-Layer Perceptron model for Wordle solving."""
import torch
import torch.nn as nn
import torch.nn.functional as F
from typing import Optional


class MLPWordleSolver(nn.Module):
    """MLP model that predicts next guess from game state."""
    
    def __init__(
        self,
        input_dim: int,
        vocab_size: int,
        hidden_dims: list = [512, 256, 128],
        dropout: float = 0.3
    ):
        """
        Initialize MLP model.
        
        Args:
            input_dim: Dimension of input state encoding
            vocab_size: Number of candidate words (output classes)
            hidden_dims: List of hidden layer dimensions
            dropout: Dropout probability
        """
        super().__init__()
        self.input_dim = input_dim
        self.vocab_size = vocab_size
        
        layers = []
        prev_dim = input_dim
        
        for hidden_dim in hidden_dims:
            layers.append(nn.Linear(prev_dim, hidden_dim))
            layers.append(nn.ReLU())
            layers.append(nn.Dropout(dropout))
            prev_dim = hidden_dim
        
        # Output layer
        layers.append(nn.Linear(prev_dim, vocab_size))
        
        self.network = nn.Sequential(*layers)
    
    def forward(self, state: torch.Tensor) -> torch.Tensor:
        """
        Forward pass.
        
        Args:
            state: Encoded game state, shape (batch_size, input_dim)
            
        Returns:
            Logits over vocabulary, shape (batch_size, vocab_size)
        """
        return self.network(state)
    
    def predict(self, state: torch.Tensor, top_k: int = 1) -> torch.Tensor:
        """
        Predict top-k words.
        
        Args:
            state: Encoded game state
            top_k: Number of top predictions to return
            
        Returns:
            Top-k word indices, shape (batch_size, top_k)
        """
        with torch.no_grad():
            logits = self.forward(state)
            probs = F.softmax(logits, dim=-1)
            top_probs, top_indices = torch.topk(probs, k=min(top_k, self.vocab_size), dim=-1)
            return top_indices


