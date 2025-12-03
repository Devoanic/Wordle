# Quick Start Guide

## Installation

```bash
pip install -r requirements.txt
```

## Step 1: Test the System

Run the demo to verify everything works:

```bash
python scripts/demo.py
```

You should see output showing:

- A sample Wordle game
- Feedback generation examples

## Step 2: Train a Model

Train a simple MLP model (this may take a few minutes):

```bash
python scripts/train.py --model mlp --epochs 20 --num-games 5000
```

This will:

- Generate 5000 simulated Wordle games
- Train an MLP model for 20 epochs
- Save the model to `models/wordle_mlp_20epochs.pt`

## Step 3: Use the Solver

### Interactive Mode

```bash
python scripts/solve.py --model models/wordle_mlp_20epochs.pt --interactive
```

Then follow the prompts:

1. Enter your guess (5 letters)
2. Enter feedback: `g` for green, `y` for yellow, `x` for gray
3. The solver will suggest the next guess

### Auto-Solve a Word

```bash
python scripts/solve.py --model models/wordle_mlp_20epochs.pt --solution apple
```

## Step 4: Evaluate Performance

```bash
# Test the ML model
python scripts/evaluate.py --model models/wordle_mlp_20epochs.pt --num-games 50

# Compare with baseline
python scripts/evaluate.py --baseline entropy --num-games 50
```

## Troubleshooting

### "Model file not found"

Make sure you've trained a model first using `scripts/train.py`

### "No valid word list"

The system uses a default word list. To use custom words, see the README.

### Training is slow

- Reduce `--num-games` for faster training (e.g., `--num-games 1000`)
- Reduce `--epochs` for fewer training iterations (e.g., `--epochs 10`)

## Next Steps

1. **Improve performance**: Train with more games (`--num-games 20000`)
2. **Try LSTM**: Use `--model lstm` instead of `mlp`
3. **Custom word lists**: Add your own word list files
4. **Tune hyperparameters**: Adjust learning rate, batch size, etc.


