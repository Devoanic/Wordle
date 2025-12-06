"""Local web server for Wordle extension communication."""
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import sys
import logging
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.game.word_manager import WordManager
from src.game.game_engine import Feedback
from src.evaluation.baseline import BaselineSolver
from scripts.solve import WordleSolver
from src.game.letter_analyzer import LetterAnalyzer
from src.game.word_tracker import track_solved_word

app = Flask(__name__)
CORS(app)  # Allow cross-origin requests from extension

# Configure logging to see all output
logging.basicConfig(level=logging.DEBUG)
app.logger.setLevel(logging.DEBUG)

# Initialize solvers
word_manager = WordManager()
baseline_solver = BaselineSolver(word_manager, strategy='entropy')
letter_analyzer = LetterAnalyzer()
ml_solver = None


def feedback_from_string(feedback_str: str):
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


@app.route('/')
def index():
    """Serve the extension helper page."""
    return send_from_directory(Path(__file__).parent.parent / 'extension', 'index.html')


@app.route('/api/suggest', methods=['POST'])
def suggest():
    """Get word suggestions based on guesses and feedback."""
    try:
        # Check ml_solver at function start
        app.logger.info(f"FUNCTION START: ml_solver is {ml_solver is not None}")
        print(f"FUNCTION START: ml_solver is {ml_solver is not None}", flush=True)
        sys.stdout.flush()
        
        data = request.json
        guesses = [g.lower() for g in data.get('guesses', [])]
        feedback_list_str = data.get('feedback', [])
        use_ml = data.get('use_ml', False)
        model_path = data.get('model_path', None)
        
        # Debug logging
        app.logger.info(f"API Request - Guesses: {guesses}, Feedback: {feedback_list_str}, use_ml: {use_ml}")
        print(f"API Request - Guesses: {guesses}, Feedback: {feedback_list_str}, use_ml: {use_ml}", flush=True)
        sys.stdout.flush()
        
        # Convert feedback strings to Feedback enums
        feedback_list = []
        for fb_str in feedback_list_str:
            feedback_list.append(feedback_from_string(fb_str))
        
        # Get suggestions and candidate count
        print(f"DEBUG: use_ml={use_ml}, ml_solver={ml_solver is not None}", flush=True)
        if use_ml and ml_solver:
            print("DEBUG: Calling get_ml_suggestions", flush=True)
            suggestions, num_candidates = get_ml_suggestions(guesses, feedback_list)
            solver_type = "ML"
        elif use_ml and not ml_solver:
            # ML requested but not available, fall back to baseline
            print("Warning: ML model requested but not loaded. Using baseline solver.", flush=True)
            suggestions, num_candidates = get_baseline_suggestions(guesses, feedback_list)
            solver_type = "Baseline (ML not available)"
        else:
            print(f"DEBUG: Using baseline (use_ml={use_ml})", flush=True)
            suggestions, num_candidates = get_baseline_suggestions(guesses, feedback_list)
            solver_type = "Baseline"
        
        print(f"API Response ({solver_type}) - Suggestions: {suggestions[:10]}, Candidates: {num_candidates}", flush=True)
        
        return jsonify({
            'success': True,
            'suggestions': suggestions[:10],
            'num_candidates': num_candidates,
            'solver_type': solver_type
        })
    
    except Exception as e:
        print(f"API Error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400


@app.route('/api/starting-words', methods=['GET'])
def starting_words():
    """Get best starting words."""
    try:
        all_words = word_manager.get_all_valid_words()
        best_words = letter_analyzer.get_best_starting_words(all_words, top_k=10)
        
        result = []
        for word, score in best_words:
            vowel_count = letter_analyzer.get_vowel_count(word)
            result.append({
                'word': word.upper(),
                'score': score,
                'vowels': vowel_count
            })
        
        return jsonify({
            'success': True,
            'words': result
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400


@app.route('/api/track-solved', methods=['POST'])
def track_solved():
    """Track a solved word."""
    try:
        data = request.json
        word = data.get('word', '').lower()
        
        if word:
            track_solved_word(word)
            letter_analyzer.refresh()
            return jsonify({
                'success': True,
                'message': f'Tracked {word.upper()}'
            })
        else:
            return jsonify({
                'success': False,
                'error': 'No word provided'
            }), 400
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400


@app.route('/api/stats', methods=['GET'])
def stats():
    """Get letter frequency statistics."""
    try:
        stats = letter_analyzer.get_letter_stats()
        return jsonify({
            'success': True,
            'stats': stats,
            'total_words': len(letter_analyzer.common_words)
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400


def get_baseline_suggestions(guesses, feedback_list):
    """Get suggestions from baseline solver."""
    # Filter out already-guessed words
    guessed_set = {g.lower() for g in guesses}
    
    next_guess = baseline_solver.solve(guesses, feedback_list)
    if not next_guess:
        return []
    
    # Get all candidates
    baseline_solver.pruner.reset()
    for guess, feedback in zip(guesses, feedback_list):
        baseline_solver.pruner.apply_feedback(guess, feedback)
    
    candidates = baseline_solver.pruner.get_candidates()
    
    # Filter out already-guessed words
    candidates = [w for w in candidates if w.lower() not in guessed_set]
    num_candidates = len(candidates)
    
    # Put solver suggestion first (if not already guessed)
    suggestions = []
    if next_guess and next_guess.lower() not in guessed_set:
        suggestions.append(next_guess)
    
    # Add other candidates
    for word in candidates:
        if word.lower() not in guessed_set and word not in suggestions:
            suggestions.append(word)
    
    return suggestions[:10], num_candidates


def get_ml_suggestions(guesses, feedback_list):
    """Get suggestions from ML solver."""
    print("=" * 60, flush=True)
    print("get_ml_suggestions CALLED!", flush=True)
    print(f"Guesses: {guesses}, Feedback length: {len(feedback_list)}", flush=True)
    print("=" * 60, flush=True)
    try:
        if not ml_solver:
            print("ERROR: ml_solver is None!")
            return get_baseline_suggestions(guesses, feedback_list)
        
        # Filter out already-guessed words
        guessed_set = {g.lower() for g in guesses}
        
        # Get ML model's top predictions
        import torch
        ml_solver.pruner.reset()
        for guess, feedback in zip(guesses, feedback_list):
            ml_solver.pruner.apply_feedback(guess, feedback)
        
        candidates = ml_solver.pruner.get_candidates()
        
        if not candidates:
            print("ERROR: No candidates!")
            return []
        
        # Get top predictions from model
        state_vec = ml_solver.state_encoder.encode_state_concatenated(guesses, feedback_list)
        state_tensor = torch.FloatTensor(state_vec).unsqueeze(0).to(ml_solver.device)
        
        with torch.no_grad():
            logits = ml_solver.model(state_tensor)
            probs = torch.softmax(logits, dim=-1)
            top_probs, top_indices = torch.topk(probs, k=min(20, len(ml_solver.all_words)))
        
        # Get top words from model predictions
        top_words = [ml_solver.all_words[idx] for idx in top_indices[0].cpu().numpy()]
        print(f"DEBUG: Top 10 model predictions: {top_words[:10]}")
        
        # Filter to valid candidates
        valid_predictions = [w for w in top_words if w in candidates and w.lower() not in guessed_set]
        print(f"DEBUG: Valid predictions (in candidates): {valid_predictions[:10]}")
        
        # Put ML suggestions first (prioritize model's top predictions)
        suggestions = []
        for word in valid_predictions:
            if word.lower() not in guessed_set and word not in suggestions:
                suggestions.append(word)
            if len(suggestions) >= 10:
                break
        
        print(f"DEBUG: Final ML suggestions: {suggestions[:10]}")
        
        # Count valid candidates (excluding already guessed)
        num_candidates = len([w for w in candidates if w.lower() not in guessed_set])
        
        if not suggestions:
            print("WARNING: No ML suggestions, falling back to baseline")
            return get_baseline_suggestions(guesses, feedback_list)
        
        return suggestions[:10], num_candidates
    except Exception as e:
        print(f"ERROR in get_ml_suggestions: {e}", flush=True)
        import traceback
        traceback.print_exc()
        print("Falling back to baseline solver due to error", flush=True)
        return get_baseline_suggestions(guesses, feedback_list)


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Wordle Solver Web Server')
    parser.add_argument('--port', type=int, default=5000, help='Port to run server on')
    parser.add_argument('--host', type=str, default='127.0.0.1', help='Host to bind to')
    parser.add_argument('--model', type=str, default=None, help='Path to ML model')
    
    args = parser.parse_args()
    
    # Initialize ML solver if model path provided
    if args.model:
        try:
            ml_solver = WordleSolver(args.model, 'mlp')
            print(f"Loaded ML model: {args.model}")
            print(f"VERIFY: ml_solver is now: {ml_solver is not None}")
        except Exception as e:
            print(f"Failed to load ML model: {e}")
            print("Using baseline solver only")
            ml_solver = None
    else:
        print("No ML model provided. Use --model flag to enable ML solver.")
        ml_solver = None
    
    # Verify ml_solver is accessible
    print(f"FINAL CHECK: ml_solver accessible in main: {ml_solver is not None}")
    
    print(f"\n{'='*60}")
    print("Wordle Solver Web Server")
    print(f"{'='*60}")
    print(f"Server running at: http://{args.host}:{args.port}")
    print(f"Extension can connect to: http://{args.host}:{args.port}/api")
    print(f"{'='*60}\n")
    
    app.run(host=args.host, port=args.port, debug=True)

