"""LSTM model for sequential Wordle solving."""
import torch
import torch.nn as nn
import torch.nn.functional as F
from typing import Optional, Tuple


class LSTMWordleSolver(nn.Module):
    """LSTM model that processes sequence of guesses and feedback."""
    
    def __init__(
        self,
        input_dim: int,
        vocab_size: int,
        hidden_dim: int = 256,
        num_layers: int = 2,
        dropout: float = 0.3
    ):
        """
        Initialize LSTM model.
        
        Args:
            input_dim: Dimension of input per timestep (guess + feedback)
            vocab_size: Number of candidate words (output classes)
            hidden_dim: LSTM hidden dimension
            num_layers: Number of LSTM layers
            dropout: Dropout probability
        """
        super().__init__()
        self.input_dim = input_dim
        self.vocab_size = vocab_size
        self.hidden_dim = hidden_dim
        self.num_layers = num_layers
        
        # LSTM to process sequence
        self.lstm = nn.LSTM(
            input_dim,
            hidden_dim,
            num_layers,
            batch_first=True,
            dropout=dropout if num_layers > 1 else 0
        )
        
        # Output layers
        self.fc1 = nn.Linear(hidden_dim, hidden_dim // 2)
        self.dropout = nn.Dropout(dropout)
        self.fc2 = nn.Linear(hidden_dim // 2, vocab_size)
    
    def forward(
        self,
        sequence: torch.Tensor,
        lengths: Optional[torch.Tensor] = None
    ) -> torch.Tensor:
        """
        Forward pass.
        
        Args:
            sequence: Encoded game state sequence, shape (batch_size, seq_len, input_dim)
            lengths: Actual sequence lengths, shape (batch_size,)
            
        Returns:
            Logits over vocabulary, shape (batch_size, vocab_size)
        """
        # Pack sequence if lengths provided
        if lengths is not None:
            packed_sequence = nn.utils.rnn.pack_padded_sequence(
                sequence, lengths.cpu(), batch_first=True, enforce_sorted=False
            )
            # LSTM forward
            lstm_out, (hidden, _) = self.lstm(packed_sequence)
            # Use last hidden state (already correctly indexed by pack_padded_sequence)
            final_hidden = hidden[-1]  # Last layer hidden state
        else:
            # LSTM forward
            lstm_out, (hidden, _) = self.lstm(sequence)
            # Use last hidden state
            final_hidden = hidden[-1]  # Last layer, shape (batch_size, hidden_dim)
        
        # Fully connected layers
        x = F.relu(self.fc1(final_hidden))
        x = self.dropout(x)
        logits = self.fc2(x)
        
        return logits
    
    def predict(
        self,
        sequence: torch.Tensor,
        lengths: Optional[torch.Tensor] = None,
        top_k: int = 1
    ) -> torch.Tensor:
        """
        Predict top-k words.
        
        Args:
            sequence: Encoded game state sequence
            lengths: Actual sequence lengths
            top_k: Number of top predictions to return
            
        Returns:
            Top-k word indices, shape (batch_size, top_k)
        """
        with torch.no_grad():
            logits = self.forward(sequence, lengths)
            probs = F.softmax(logits, dim=-1)
            top_probs, top_indices = torch.topk(probs, k=min(top_k, self.vocab_size), dim=-1)
            return top_indices

