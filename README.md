# Efficient Python Spell Checker with Wagner-Fischer Optimization

[![Python Version](https://img.shields.io/badge/python-3.7%2B-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Overview

This project implements a highly efficient spell-checking suggestion system in Python. It leverages the **Wagner-Fischer algorithm** to compute the **Levenshtein distance** (minimum edit distance) between strings. Crucially, this implementation goes beyond a naive approach by incorporating significant performance optimizations, making it suitable for scenarios involving large dictionaries often encountered in Natural Language Processing (NLP) and data cleansing tasks.

The core goal is to provide accurate spelling suggestions rapidly, demonstrating an understanding of both fundamental string algorithms and practical performance engineering.

## Key Features

*   **Accurate Edit Distance:** Implements the classic Wagner-Fischer algorithm for precise Levenshtein distance calculation (insertions, deletions, substitutions).
*   **Performance Optimized:** Incorporates several heuristics and data structures to significantly speed up the suggestion process compared to brute-force comparison against a large dictionary.
    *   **Length Pruning:** Avoids distance calculation for words with length differences exceeding the maximum allowed edits.
    *   **Max Distance Thresholding:** Filters candidates early based on a maximum acceptable Levenshtein distance.
    *   **Optimized Wagner-Fischer:** Includes an early exit mechanism within the distance calculation if the threshold is guaranteed to be exceeded.
    *   **Efficient Top-K Selection:** Utilizes Python's `heapq` (min-heap) module to efficiently find the N best suggestions without needing to sort the entire potential candidate list (O(D log N) heap complexity vs O(D log D) sorting, where D is dictionary size and N is the number of suggestions).
*   **Customizable:** Allows configuration of the number of suggestions (`num_suggestions`) and the maximum edit distance (`max_edit_distance`) to consider.
*   **Clean & Readable Code:** Uses type hinting and clear docstrings for maintainability and understanding.
*   **Standard Library:** Relies only on Python's standard library (no external dependencies needed beyond a dictionary file).

## Algorithmic Foundation: Wagner-Fischer & Levenshtein Distance

The heart of the spell checker is the **Levenshtein distance**, a metric defining the minimum number of single-character edits (insertions, deletions, or substitutions) required to change one word into another.

The **Wagner-Fischer algorithm** is a standard dynamic programming approach to compute this distance. It constructs a matrix where `matrix[i][j]` represents the Levenshtein distance between the first `i` characters of string `s2` and the first `j` characters of string `s1`. Each cell is computed based on the minimum cost of reaching it via:

1.  **Insertion:** `matrix[i][j-1] + 1`
2.  **Deletion:** `matrix[i-1][j] + 1`
3.  **Substitution:** `matrix[i-1][j-1] + cost` (cost is 0 if characters match, 1 otherwise)

This implementation uses a space-optimized version that only requires storing the previous and current rows of the conceptual matrix, reducing space complexity from O(m*n) to O(min(m,n)).

## Performance Optimizations Explained

While Wagner-Fischer is correct, computing it for a misspelled word against every word in a large dictionary can be computationally expensive. This implementation tackles this challenge:

1.  **Length Difference Pruning:** The Levenshtein distance between two strings is always *at least* the absolute difference in their lengths. If `abs(len(word1) - len(word2)) > max_edit_distance`, we can immediately discard `word2` as a candidate without running Wagner-Fischer.
2.  **Early Exit in Wagner-Fischer:** The `wagner_fischer` function accepts a `max_distance` threshold. During the dynamic programming calculation, if the minimum value computed in the current row already exceeds this `max_distance`, the function terminates early, as the final distance is guaranteed to be too large.
3.  **Efficient Top-K Retrieval (`heapq`):** Instead of calculating distances for all potential candidates (those passing the length filter) and then sorting the entire list (O(D log D)), we iterate through candidates. For each candidate within the `max_edit_distance`, we add `(distance, word)` to a list. Finally, `heapq.nsmallest(num_suggestions, candidates)` efficiently extracts the best N suggestions in O(C + N log N) or O(C log N) time depending on the implementation details (where C is the number of candidates passing the distance filter, typically C << D). This is significantly faster for large dictionaries (D) when seeking a small number of suggestions (N).

## Installation & Setup

1.  **Clone the repository:**
    ```bash
    git clone <your-repo-url>
    cd <your-repo-directory>
    ```
2.  **Ensure Python 3.7+ is installed.**
3.  **Obtain a Dictionary File:** You need a plain text file containing a list of correctly spelled words, one word per line. Name this file `words.txt` and place it in the same directory as the Python script, or update the `DICTIONARY_FILE` constant in the script. Common sources include `/usr/share/dict/words` on Linux/macOS or online wordlists.

## Usage

```python
from spell_checker import load_dictionary, spell_check # Assuming your file is named spell_checker.py

# --- Configuration ---
DICTIONARY_FILE = "words.txt"
NUM_SUGGESTIONS = 10
MAX_EDIT_DIST = 3

# --- Load Dictionary ---
try:
    print(f"Loading dictionary from {DICTIONARY_FILE}...")
    dictionary = load_dictionary(DICTIONARY_FILE)
    print(f"Dictionary loaded with {len(dictionary)} words.")
except FileNotFoundError:
    print(f"Error: Dictionary file '{DICTIONARY_FILE}' not found.")
    exit()
except Exception as e:
    print(f"An error occurred loading the dictionary: {e}")
    exit()

# --- Perform Spell Check ---
misspelled_word = "wrlod"

print(f"\nFinding suggestions for '{misspelled_word}'...")
suggestions = spell_check(
    word=misspelled_word,
    dictionary=dictionary,
    num_suggestions=NUM_SUGGESTIONS,
    max_edit_distance=MAX_EDIT_DIST
)

# --- Display Results ---
print(f"\nTop {NUM_SUGGESTIONS} suggestions for '{misspelled_word}' (max distance {MAX_EDIT_DIST}):")
if suggestions:
    for suggested_word, distance in suggestions:
        print(f"- {suggested_word} (Distance: {distance})")
else:
    print("No suggestions found within the maximum edit distance.")

# Example with different parameters:
suggestions_alt = spell_check("recieve", dictionary, num_suggestions=5, max_edit_distance=2)
print(f"\nTop 5 suggestions for 'recieve' (max distance 2):")
# ... (display logic) ...
