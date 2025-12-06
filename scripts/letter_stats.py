"""Display letter frequency statistics and best starting words."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.game.word_manager import WordManager
from src.game.letter_analyzer import LetterAnalyzer


def print_letter_stats():
    """Print comprehensive letter frequency statistics."""
    analyzer = LetterAnalyzer()
    stats = analyzer.get_letter_stats()
    
    print("\n" + "="*70)
    print("LETTER FREQUENCY STATISTICS (Based on Common Wordle Solutions)")
    print("="*70)
    print(f"\nTotal common solutions analyzed: {len(analyzer.common_words)}")
    print("\nLetter Frequency (Overall):")
    print("-" * 70)
    
    # Sort by frequency
    sorted_letters = sorted(stats.items(), key=lambda x: x[1]['frequency'], reverse=True)
    
    print(f"{'Letter':<8} {'Frequency':<12} {'Percentage':<12} {'Most Common Pos':<15} {'Vowel'}")
    print("-" * 70)
    
    for letter, data in sorted_letters:
        pos_str = f"Position {data['most_common_position'] + 1}" if data['most_common_position'] >= 0 else "N/A"
        vowel_str = "Yes" if data['is_vowel'] else "No"
        print(f"{letter.upper():<8} {data['frequency']:<12} {data['percentage']:>6.2f}%      {pos_str:<15} {vowel_str}")
    
    print("\n" + "="*70)
    print("TOP 10 LETTERS BY FREQUENCY:")
    print("-" * 70)
    for i, (letter, data) in enumerate(sorted_letters[:10], 1):
        print(f"{i}. {letter.upper()}: {data['frequency']} occurrences ({data['percentage']:.2f}%)")
    
    print("\n" + "="*70)
    print("VOWEL STATISTICS:")
    print("-" * 70)
    vowels = [('a', stats['a']), ('e', stats['e']), ('i', stats['i']), ('o', stats['o']), ('u', stats['u'])]
    vowels_sorted = sorted(vowels, key=lambda x: x[1]['frequency'], reverse=True)
    for letter, data in vowels_sorted:
        print(f"{letter.upper()}: {data['frequency']} occurrences ({data['percentage']:.2f}%)")


def print_best_starting_words():
    """Print best starting words based on letter frequency."""
    word_manager = WordManager()
    all_words = word_manager.get_all_valid_words()
    
    analyzer = LetterAnalyzer()
    best_words = analyzer.get_best_starting_words(all_words, top_k=20)
    
    print("\n" + "="*70)
    print("BEST STARTING WORDS (Based on Letter Frequency Analysis)")
    print("="*70)
    print("\nThese words have:")
    print("  - High frequency letters")
    print("  - Good vowel distribution (2-3 vowels)")
    print("  - Unique letters (no duplicates)")
    print("  - Letters in common positions")
    print("\n" + "-" * 70)
    print(f"{'Rank':<6} {'Word':<10} {'Score':<12} {'Vowels':<8} {'Unique Letters'}")
    print("-" * 70)
    
    for i, (word, score) in enumerate(best_words, 1):
        vowel_count = analyzer.get_vowel_count(word)
        unique_count = len(set(word))
        print(f"{i:<6} {word.upper():<10} {score:>10.1f}   {vowel_count:<8} {unique_count}")
    
    print("\n" + "="*70)


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Wordle Letter Statistics')
    parser.add_argument('--stats', action='store_true', help='Show letter frequency statistics')
    parser.add_argument('--words', action='store_true', help='Show best starting words')
    parser.add_argument('--all', action='store_true', help='Show everything')
    
    args = parser.parse_args()
    
    if args.all or (not args.stats and not args.words):
        print_letter_stats()
        print_best_starting_words()
    else:
        if args.stats:
            print_letter_stats()
        if args.words:
            print_best_starting_words()


if __name__ == '__main__':
    main()


