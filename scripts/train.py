"""Training script for Wordle solver."""
import argparse
import os
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.game.word_manager import WordManager
from src.features.state_encoder import StateEncoder
from src.models.mlp_model import MLPWordleSolver
from src.models.lstm_model import LSTMWordleSolver
from src.training.data_generator import DataGenerator
from src.training.trainer import Trainer, WordleDataset
from torch.utils.data import DataLoader, random_split
import torch
import numpy as np


def main():
    parser = argparse.ArgumentParser(description='Train Wordle Solver')
    parser.add_argument('--model', type=str, default='mlp', choices=['mlp', 'lstm'],
                        help='Model architecture')
    parser.add_argument('--epochs', type=int, default=50, help='Number of epochs')
    parser.add_argument('--batch-size', type=int, default=64, help='Batch size')
    parser.add_argument('--learning-rate', type=float, default=0.001, help='Learning rate')
    parser.add_argument('--num-games', type=int, default=10000, help='Number of training games')
    parser.add_argument('--val-split', type=float, default=0.2, help='Validation split')
    parser.add_argument('--save-dir', type=str, default='models', help='Model save directory')
    parser.add_argument('--word-list', type=str, default=None, help='Path to word list file')
    
    args = parser.parse_args()
    
    # Create directories
    os.makedirs(args.save_dir, exist_ok=True)
    
    # Initialize word manager
    print("Initializing word manager...")
    word_manager = WordManager()
    if not word_manager.solutions:
        word_manager.generate_default_word_list()
    
    # Load training solutions if provided
    training_solutions = None
    if args.word_list:
        print(f"Loading training solutions from {args.word_list}...")
        training_solutions = []
        with open(args.word_list, 'r', encoding='utf-8') as f:
            for line in f:
                word = line.strip().upper()
                if len(word) == 5 and word.isalpha():
                    training_solutions.append(word.lower())
        print(f"Loaded {len(training_solutions)} training solutions")
    else:
        # Try to load default training solutions
        training_file = Path(__file__).parent.parent / 'word_lists' / 'training_solutions.txt'
        if training_file.exists():
            print(f"Loading training solutions from {training_file}...")
            training_solutions = []
            with open(training_file, 'r', encoding='utf-8') as f:
                for line in f:
                    word = line.strip().upper()
                    if len(word) == 5 and word.isalpha():
                        training_solutions.append(word.lower())
            print(f"Loaded {len(training_solutions)} training solutions")
        else:
            print("No training solutions file found, using random solutions from word list")
    
    # Initialize state encoder
    state_encoder = StateEncoder(word_length=5, max_guesses=6)
    
    # Calculate input dimension
    guess_dim = 5 * 26  # word_length * alphabet_size
    feedback_dim = 5
    input_dim = 6 * (guess_dim + feedback_dim)  # max_guesses * (guess + feedback)
    
    vocab_size = len(word_manager.get_all_valid_words())
    
    print(f"Vocabulary size: {vocab_size}")
    print(f"Input dimension: {input_dim}")
    
    # Create model
    print(f"Creating {args.model.upper()} model...")
    if args.model == 'mlp':
        model = MLPWordleSolver(
            input_dim=input_dim,
            vocab_size=vocab_size,
            hidden_dims=[512, 256, 128],
            dropout=0.3
        )
    else:  # lstm
        seq_input_dim = guess_dim + feedback_dim
        model = LSTMWordleSolver(
            input_dim=seq_input_dim,
            vocab_size=vocab_size,
            hidden_dim=256,
            num_layers=2,
            dropout=0.3
        )
    
    print(f"Model parameters: {sum(p.numel() for p in model.parameters()):,}")
    
    # Generate training data
    print(f"\nGenerating {args.num_games} training games...")
    if training_solutions:
        print(f"Using {len(training_solutions)} specific solution words")
    data_generator = DataGenerator(word_manager, state_encoder, strategy='random')
    
    states, targets = data_generator.generate_dataset(args.num_games, solutions=training_solutions)
    print(f"Generated {len(states)} training samples")
    
    # Create dataset and split
    dataset = WordleDataset(states, targets)
    val_size = int(len(dataset) * args.val_split)
    train_size = len(dataset) - val_size
    train_dataset, val_dataset = random_split(dataset, [train_size, val_size])
    
    train_loader = DataLoader(train_dataset, batch_size=args.batch_size, shuffle=True)
    val_loader = DataLoader(val_dataset, batch_size=args.batch_size, shuffle=False)
    
    # Train
    trainer = Trainer(
        model=model,
        learning_rate=args.learning_rate,
        weight_decay=1e-5
    )
    
    model_name = f"wordle_{args.model}_{args.epochs}epochs.pt"
    save_path = os.path.join(args.save_dir, model_name)
    
    print(f"\nStarting training...")
    print(f"Model will be saved to: {save_path}")
    
    history = trainer.train(
        train_loader=train_loader,
        val_loader=val_loader,
        epochs=args.epochs,
        save_path=save_path
    )
    
    print(f"\nTraining complete! Best model saved to {save_path}")


if __name__ == '__main__':
    main()




