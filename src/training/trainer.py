"""Training utilities for Wordle solver models."""
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader
import numpy as np
from typing import Optional, Dict
from tqdm import tqdm


class WordleDataset(Dataset):
    """Dataset for Wordle training data."""
    
    def __init__(self, states: np.ndarray, targets: np.ndarray):
        """
        Initialize dataset.
        
        Args:
            states: Encoded game states, shape (N, state_dim)
            targets: Target word indices, shape (N,)
        """
        self.states = torch.FloatTensor(states)
        self.targets = torch.LongTensor(targets)
    
    def __len__(self) -> int:
        return len(self.states)
    
    def __getitem__(self, idx: int) -> tuple:
        return self.states[idx], self.targets[idx]


class Trainer:
    """Trainer for Wordle solver models."""
    
    def __init__(
        self,
        model: nn.Module,
        device: str = None,
        learning_rate: float = 0.001,
        weight_decay: float = 1e-5
    ):
        """
        Initialize trainer.
        
        Args:
            model: Model to train
            device: 'cpu' or 'cuda' (auto-detect if None)
            learning_rate: Learning rate for optimizer
            weight_decay: Weight decay for regularization
        """
        self.model = model
        self.device = device or ('cuda' if torch.cuda.is_available() else 'cpu')
        self.model.to(self.device)
        
        self.optimizer = optim.Adam(
            self.model.parameters(),
            lr=learning_rate,
            weight_decay=weight_decay
        )
        self.criterion = nn.CrossEntropyLoss()
        
        self.train_losses = []
        self.val_losses = []
    
    def train_epoch(
        self,
        dataloader: DataLoader,
        verbose: bool = True
    ) -> float:
        """
        Train for one epoch.
        
        Returns:
            Average training loss
        """
        self.model.train()
        total_loss = 0.0
        num_batches = 0
        
        iterator = tqdm(dataloader, desc='Training') if verbose else dataloader
        
        for states, targets in iterator:
            states = states.to(self.device)
            targets = targets.to(self.device)
            
            # Forward pass
            self.optimizer.zero_grad()
            logits = self.model(states)
            loss = self.criterion(logits, targets)
            
            # Backward pass
            loss.backward()
            self.optimizer.step()
            
            total_loss += loss.item()
            num_batches += 1
        
        avg_loss = total_loss / num_batches if num_batches > 0 else 0.0
        self.train_losses.append(avg_loss)
        return avg_loss
    
    def validate(
        self,
        dataloader: DataLoader
    ) -> Dict[str, float]:
        """
        Validate model.
        
        Returns:
            Dictionary with validation metrics
        """
        self.model.eval()
        total_loss = 0.0
        correct = 0
        total = 0
        
        with torch.no_grad():
            for states, targets in dataloader:
                states = states.to(self.device)
                targets = targets.to(self.device)
                
                logits = self.model(states)
                loss = self.criterion(logits, targets)
                
                total_loss += loss.item()
                
                # Accuracy
                predictions = torch.argmax(logits, dim=-1)
                correct += (predictions == targets).sum().item()
                total += targets.size(0)
        
        avg_loss = total_loss / len(dataloader)
        accuracy = correct / total if total > 0 else 0.0
        
        self.val_losses.append(avg_loss)
        
        return {
            'loss': avg_loss,
            'accuracy': accuracy
        }
    
    def train(
        self,
        train_loader: DataLoader,
        val_loader: Optional[DataLoader] = None,
        epochs: int = 10,
        save_path: Optional[str] = None
    ) -> Dict[str, list]:
        """
        Train model for multiple epochs.
        
        Args:
            train_loader: Training data loader
            val_loader: Validation data loader (optional)
            epochs: Number of epochs
            save_path: Path to save best model
            
        Returns:
            Dictionary with training history
        """
        best_val_loss = float('inf')
        
        for epoch in range(epochs):
            print(f"\nEpoch {epoch + 1}/{epochs}")
            
            # Train
            train_loss = self.train_epoch(train_loader)
            print(f"Train Loss: {train_loss:.4f}")
            
            # Validate
            if val_loader:
                val_metrics = self.validate(val_loader)
                print(f"Val Loss: {val_metrics['loss']:.4f}, "
                      f"Val Accuracy: {val_metrics['accuracy']:.4f}")
                
                # Save best model
                if save_path and val_metrics['loss'] < best_val_loss:
                    best_val_loss = val_metrics['loss']
                    torch.save({
                        'model_state_dict': self.model.state_dict(),
                        'optimizer_state_dict': self.optimizer.state_dict(),
                        'epoch': epoch,
                        'loss': best_val_loss
                    }, save_path)
                    print(f"Saved best model to {save_path}")
        
        return {
            'train_losses': self.train_losses,
            'val_losses': self.val_losses
        }





