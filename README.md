# ML Wordle Solver

An intelligent Wordle solver using machine learning to predict optimal guesses based on game history.

## Features

- **Game Engine**: Complete Wordle game implementation with feedback generation
- **ML Models**: Multiple architectures (MLP, LSTM) for next-guess prediction
- **Candidate Pruning**: Efficient word filtering based on feedback constraints
- **Training System**: Automated data generation and model training
- **Evaluation Metrics**: Comprehensive performance analysis
- **CLI Interface**: Interactive solver for real-time gameplay
- **Overlay Assistant**: GUI overlay that stays on top while playing Wordle

## Project Structure

```
Wordle/
├── word_lists/          # Word lists (solutions and allowed guesses)
├── src/
│   ├── game/           # Game engine and feedback
│   ├── models/         # ML model architectures
│   ├── features/       # Feature encoding
│   ├── training/       # Training scripts
│   └── evaluation/     # Evaluation metrics
├── data/               # Generated training data
├── models/             # Trained model checkpoints
└── scripts/            # CLI and utility scripts
```

## Installation

```bash
pip install -r requirements.txt
```

## Quick Start

### 1. Test the Game Engine

```bash
python scripts/demo.py
```

This runs a quick demo of the game engine and feedback generation.

### 2. Training a Model

Train an MLP model with default settings:

```bash
python scripts/train.py --model mlp --epochs 50 --num-games 10000
```

Train an LSTM model:

```bash
python scripts/train.py --model lstm --epochs 50 --num-games 10000
```

**Training Options:**

- `--model`: Model architecture (`mlp` or `lstm`)
- `--epochs`: Number of training epochs (default: 50)
- `--batch-size`: Batch size (default: 64)
- `--learning-rate`: Learning rate (default: 0.001)
- `--num-games`: Number of simulated games for training (default: 10000)
- `--val-split`: Validation split ratio (default: 0.2)
- `--save-dir`: Directory to save models (default: `models/`)

### 3. Using the Solver

**Interactive Mode** (you provide guesses and feedback):

```bash
python scripts/solve.py --model models/wordle_mlp_50epochs.pt --interactive
```

**Auto-Solve Mode** (solves a specific word):

```bash
python scripts/solve.py --model models/wordle_mlp_50epochs.pt --solution apple
```

### 4. Overlay Assistant (Real-time Wordle Helper)

**Perfect for playing the actual Wordle game!** The overlay window stays on top and provides suggestions as you play.

**With Baseline Solver** (no training needed):

```bash
python scripts/overlay.py
```

**With ML Model**:

```bash
python scripts/overlay.py --model models/wordle_mlp_50epochs.pt
```

**Options:**

- `--model`: Path to ML model (uses baseline if not provided)
- `--model-type`: `mlp` or `lstm` (default: `mlp`)
- `--strategy`: Baseline strategy: `entropy`, `frequency`, or `random` (default: `entropy`)

**How to use:**

1. Open the Wordle game in your browser
2. Run the overlay script
3. Enter your guess and feedback (G/Y/X) after each turn
4. Get top 5 suggestions instantly!
5. The window stays on top so you can see suggestions while playing

**Feedback Format:**

- `G` or `2` = Green (correct letter, correct position)
- `Y` or `1` = Yellow (correct letter, wrong position)
- `X` or `0` = Gray (letter not in word)

Example: After guessing "CRANE" and getting feedback, enter `GYXXG` or `21002`

### 5. Evaluation

Compare ML model against baseline:

```bash
# Evaluate ML model
python scripts/evaluate.py --model models/wordle_mlp_50epochs.pt --num-games 100

# Evaluate baseline solver
python scripts/evaluate.py --baseline entropy --num-games 100

# Compare both
python scripts/evaluate.py --model models/wordle_mlp_50epochs.pt --baseline entropy --num-games 100
```

## Usage Examples

### Interactive Solving

1. Run the solver in interactive mode
2. Enter your guess when prompted
3. Enter feedback using:
   - `g` = green (correct letter, correct position)
   - `y` = yellow (correct letter, wrong position)
   - `x` = gray (letter not in word)
   - Or use numbers: `2`=green, `1`=yellow, `0`=gray

Example:

```
Turn 1/6 - Enter your guess: crane
Enter feedback (gyxxg or 21002): xxxxx
🤖 Suggested guess: SLATE
```

### Word Lists

To use custom word lists, create text files in `word_lists/`:

- One word per line
- All lowercase
- 5 letters only

Then modify the `WordManager` initialization to load from these files.

## Architecture

### MLP Model

- Input: Concatenated game state (all guesses + feedback)
- Hidden layers: 512 → 256 → 128
- Output: Probability distribution over vocabulary

### LSTM Model

- Input: Sequence of (guess + feedback) pairs
- LSTM layers: 2 layers, 256 hidden units
- Output: Probability distribution over vocabulary

### Candidate Pruning

After each guess, the solver prunes invalid words based on:

- Green constraints (exact position matches)
- Yellow constraints (letter exists but wrong position)
- Gray constraints (letter not in word)
- Letter count constraints (handles duplicate letters)

## Development

### Project Structure

- `src/game/`: Core game logic, feedback generation, candidate pruning
- `src/features/`: Word and state encoding utilities
- `src/models/`: Neural network architectures
- `src/training/`: Data generation and training utilities
- `src/evaluation/`: Evaluation metrics and baseline solvers
- `scripts/`: Command-line tools for training, solving, and evaluation

## License

MIT
