#!/usr/bin/env python3
"""
Simple Braille Autocorrect System
=================================

A beginner-friendly Braille autocorrect system for QWERTY keyboard input.
Focuses on clear, readable code with essential features.
"""

import json
from typing import List, Dict, Tuple

# Map QWERTY keys to Braille dots
BRAILLE_KEYS = {
    'D': 1, 'W': 2, 'Q': 3,  # Left side dots
    'K': 4, 'O': 5, 'P': 6   # Right side dots
}

# Map dot patterns to letters
DOT_TO_LETTER = {
    (1,): 'a', (1, 2): 'b', (1, 4): 'c', (1, 4, 5): 'd', (1, 5): 'e',
    (1, 2, 4): 'f', (1, 2, 4, 5): 'g', (1, 2, 5): 'h', (2, 4): 'i', (2, 4, 5): 'j',
    (1, 3): 'k', (1, 2, 3): 'l', (1, 3, 4): 'm', (1, 3, 4, 5): 'n', (1, 3, 5): 'o',
    (1, 2, 3, 4): 'p', (1, 2, 3, 4, 5): 'q', (1, 2, 3, 5): 'r', (2, 3, 4): 's', (2, 3, 4, 5): 't',
    (1, 3, 6): 'u', (1, 2, 3, 6): 'v', (2, 4, 5, 6): 'w', (1, 3, 4, 6): 'x', (1, 3, 4, 5, 6): 'y',
    (1, 3, 5, 6): 'z'
}

class SimpleBrailleAutocorrect:
    """Simple Braille autocorrect with basic features"""
    
    def __init__(self):
        # Dictionary of valid words
        self.dictionary = set()
        # Track word usage for better suggestions
        self.word_count = {}
        # Remember user corrections
        self.learned_fixes = {}
        
        # Add common English words
        self.load_basic_words()
    
    def load_basic_words(self):
        """Load common English words into dictionary"""
        words = [
            'the', 'and', 'for', 'are', 'but', 'not', 'you', 'all', 'can', 'had',
            'her', 'was', 'one', 'our', 'out', 'day', 'get', 'has', 'him', 'his',
            'how', 'man', 'new', 'now', 'old', 'see', 'two', 'way', 'who', 'boy',
            'did', 'its', 'let', 'put', 'say', 'she', 'too', 'use', 'good', 'have',
            'just', 'like', 'over', 'also', 'back', 'call', 'came', 'each', 'find',
            'give', 'hand', 'here', 'keep', 'kind', 'know', 'last', 'left', 'life',
            'live', 'look', 'made', 'make', 'most', 'move', 'must', 'name', 'need',
            'only', 'open', 'part', 'play', 'right', 'said', 'same', 'seem', 'show',
            'side', 'take', 'tell', 'turn', 'want', 'well', 'went', 'were', 'what',
            'when', 'where', 'which', 'will', 'with', 'word', 'work', 'world', 'year',
            'hello', 'computer', 'braille', 'system', 'keyboard', 'typing', 'input'
        ]
        
        for word in words:
            self.add_word(word)
    
    def add_word(self, word):
        """Add a word to the dictionary"""
        word = word.lower().strip()
        if word:
            self.dictionary.add(word)
            self.word_count[word] = self.word_count.get(word, 0) + 1
    
    def convert_braille_input(self, input_text):
        """Convert QWERTY Braille input to regular text"""
        result = []
        current_dots = set()
        
        for char in input_text.upper():
            if char == ' ':
                # End of character, convert dots to letter
                if current_dots:
                    letter = self.dots_to_letter(current_dots)
                    result.append(letter)
                    current_dots = set()
                result.append(' ')
            elif char in BRAILLE_KEYS:
                # Add dot to current character
                current_dots.add(BRAILLE_KEYS[char])
            else:
                # Regular character, add as-is
                if current_dots:
                    letter = self.dots_to_letter(current_dots)
                    result.append(letter)
                    current_dots = set()
                result.append(char.lower())
        
        # Handle any remaining dots
        if current_dots:
            letter = self.dots_to_letter(current_dots)
            result.append(letter)
        
        return ''.join(result)
    
    def dots_to_letter(self, dots):
        """Convert set of dots to a letter"""
        dot_pattern = tuple(sorted(dots))
        return DOT_TO_LETTER.get(dot_pattern, '?')
    
    def calculate_similarity(self, word1, word2):
        """Calculate how similar two words are (simple version)"""
        if word1 == word2:
            return 0
        
        # Simple edit distance calculation
        len1, len2 = len(word1), len(word2)
        
        # Create a matrix to store distances
        matrix = [[0] * (len2 + 1) for _ in range(len1 + 1)]
        
        # Fill first row and column
        for i in range(len1 + 1):
            matrix[i][0] = i
        for j in range(len2 + 1):
            matrix[0][j] = j
        
        # Fill the matrix
        for i in range(1, len1 + 1):
            for j in range(1, len2 + 1):
                if word1[i-1] == word2[j-1]:
                    cost = 0
                else:
                    cost = 1
                
                matrix[i][j] = min(
                    matrix[i-1][j] + 1,      # deletion
                    matrix[i][j-1] + 1,      # insertion
                    matrix[i-1][j-1] + cost  # substitution
                )
        
        return matrix[len1][len2]
    
    def find_suggestions(self, word, max_suggestions=5):
        """Find suggestions for a misspelled word"""
        word = word.lower()
        
        # If word is in dictionary, return it
        if word in self.dictionary:
            return [word]
        
        # Check if we've learned a fix for this word
        if word in self.learned_fixes:
            return [self.learned_fixes[word]]
        
        # Find similar words
        suggestions = []
        max_distance = min(3, len(word) // 2 + 1)  # Allow more errors for longer words
        
        for dict_word in self.dictionary:
            distance = self.calculate_similarity(word, dict_word)
            if distance <= max_distance:
                # Calculate score based on similarity and word frequency
                similarity_score = 1.0 - (distance / max(len(word), len(dict_word)))
                frequency_score = self.word_count.get(dict_word, 1)
                total_score = similarity_score * 0.7 + (frequency_score / 100) * 0.3
                
                suggestions.append((dict_word, total_score, distance))
        
        # Sort by score (higher is better)
        suggestions.sort(key=lambda x: x[1], reverse=True)
        
        # Return just the words
        return [word for word, score, distance in suggestions[:max_suggestions]]
    
    def autocorrect(self, text, max_suggestions=3):
        """Main autocorrect function"""
        # Convert Braille input if needed
        if any(c in 'DWQKOP' for c in text.upper()):
            text = self.convert_braille_input(text)
        
        # Process each word
        words = text.split()
        results = []
        
        for word in words:
            # Clean the word (remove punctuation for checking)
            clean_word = ''.join(c for c in word if c.isalpha())
            
            if clean_word:
                suggestions = self.find_suggestions(clean_word, max_suggestions)
                if suggestions:
                    results.append({
                        'original': word,
                        'suggestions': suggestions,
                        'best_match': suggestions[0]
                    })
                else:
                    results.append({
                        'original': word,
                        'suggestions': [],
                        'best_match': word
                    })
            else:
                results.append({
                    'original': word,
                    'suggestions': [word],
                    'best_match': word
                })
        
        return results
    
    def learn_correction(self, wrong_word, correct_word):
        """Learn from user corrections"""
        wrong_word = wrong_word.lower()
        correct_word = correct_word.lower()
        
        # Remember this correction
        self.learned_fixes[wrong_word] = correct_word
        
        # Add correct word to dictionary if not already there
        self.add_word(correct_word)
    
    def get_stats(self):
        """Get simple statistics about the system"""
        return {
            'total_words': len(self.dictionary),
            'learned_corrections': len(self.learned_fixes),
            'most_common_words': sorted(self.word_count.items(), 
                                      key=lambda x: x[1], reverse=True)[:5]
        }

def demo():
    """Simple demonstration of the system"""
    print("=== Simple Braille Autocorrect Demo ===\n")
    
    autocorrect = SimpleBrailleAutocorrect()
    
    # Test cases
    test_inputs = [
        "DK",           # Braille: D+K = dots 1,4 = 'c'
        "DW",           # Braille: D+W = dots 1,2 = 'b'  
        "helo",         # Typo: should be 'hello'
        "wrold",        # Typo: should be 'world'
        "computr",      # Missing letter: should be 'computer'
        "DW hello",     # Mixed Braille and regular text
        "the quck brown fox"  # Multiple typos
    ]
    
    for test_input in test_inputs:
        print(f"Input: '{test_input}'")
        results = autocorrect.autocorrect(test_input)
        
        corrected_text = []
        for result in results:
            if result['suggestions']:
                corrected_text.append(result['best_match'])
                if result['original'] != result['best_match']:
                    print(f"  '{result['original']}' -> '{result['best_match']}'")
                    if len(result['suggestions']) > 1:
                        print(f"    Other suggestions: {result['suggestions'][1:]}")
            else:
                corrected_text.append(result['original'])
        
        print(f"Corrected: '{' '.join(corrected_text)}'")
        print("-" * 40)
    
    # Demonstrate learning
    print("\n=== Learning Example ===")
    print("Teaching system that 'helo' should be 'hello'")
    autocorrect.learn_correction("helo", "hello")
    
    # Test again
    result = autocorrect.autocorrect("helo")
    print(f"After learning: 'helo' -> '{result[0]['best_match']}'")
    
    # Show stats
    print(f"\n=== System Stats ===")
    stats = autocorrect.get_stats()
    print(f"Total words in dictionary: {stats['total_words']}")
    print(f"Learned corrections: {stats['learned_corrections']}")
    print(f"Most common words: {[word for word, count in stats['most_common_words']]}")

if __name__ == "__main__":
    demo()