import heapq
from typing import List, Tuple, Optional

def load_dictionary(file_path: str) -> List[str]:
    """Loads a dictionary from a file, returning a list of words.

    Args:
        file_path: The path to the dictionary file (one word per line).

    Returns:
        A list of words from the file.

    Raises:
        FileNotFoundError: If the file_path does not exist.
        IOError: If there's an error reading the file.
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as file: # Specify encoding
            # Using a list comprehension for conciseness
            return [line.strip() for line in file if line.strip()] # Ensure not adding empty lines
    except FileNotFoundError:
        print(f"Error: Dictionary file not found at '{file_path}'")
        raise # Re-raise the exception
    except IOError as e:
        print(f"Error reading dictionary file '{file_path}': {e}")
        raise # Re-raise the exception


def wagner_fischer(s1: str, s2: str, max_distance: Optional[int] = None) -> int:
    """
    Calculates the Levenshtein distance between two strings using the
    Wagner-Fischer algorithm (space-optimized).

    Includes an optional optimization to exit early if the minimum distance
    in a row exceeds a specified maximum distance.

    Args:
        s1: The first string.
        s2: The second string.
        max_distance: An optional threshold. If the calculated distance is
                      guaranteed to exceed this value, the function may
                      return a value > max_distance early. If None, no
                      threshold is applied.

    Returns:
        The Levenshtein distance between s1 and s2. If max_distance is set
        and the distance exceeds it, might return a value greater than
        max_distance (often max_distance + 1 or float('inf')).
    """
    len_s1, len_s2 = len(s1), len(s2)

    # Ensure s1 is the shorter string to optimize space
    if len_s1 > len_s2:
        s1, s2 = s2, s1
        len_s1, len_s2 = len_s2, len_s1

    # Optimization: Check length difference against max_distance
    # The distance cannot be less than the difference in lengths.
    if max_distance is not None and len_s2 - len_s1 > max_distance:
        return max_distance + 1 # Impossible to be within threshold

    # Initialize the current row (representing distances from empty string to prefixes of s1)
    current_row = list(range(len_s1 + 1)) # Use list() for clarity

    # Iterate through rows (characters of s2)
    for i in range(1, len_s2 + 1):
        previous_row = current_row
        # Initialize the next row, starting with distance from empty string to s2[:i]
        current_row = [i] * (len_s1 + 1) # Create new list instance
        min_in_row = i # Keep track of minimum distance in the current row for early exit

        # Iterate through columns (characters of s1)
        for j in range(1, len_s1 + 1):
            # Calculate costs for insertion, deletion, and substitution
            insertion_cost = current_row[j - 1] + 1
            deletion_cost = previous_row[j] + 1
            substitution_cost = previous_row[j - 1] + (0 if s1[j - 1] == s2[i - 1] else 1)

            # Choose the minimum cost
            current_row[j] = min(insertion_cost, deletion_cost, substitution_cost)

            # Update minimum value found in this row
            if current_row[j] < min_in_row:
                min_in_row = current_row[j]

        # Early exit optimization: If the minimum distance calculated in this row
        # already exceeds the maximum allowed distance, the final distance (bottom-right)
        # definitely will too. We can stop early.
        if max_distance is not None and min_in_row > max_distance:
            return max_distance + 1 # Signal exceeded threshold

    # The final distance is the last element in the current_row
    final_distance = current_row[len_s1]

    # Final check against max_distance if it was provided
    if max_distance is not None and final_distance > max_distance:
        return max_distance + 1
    else:
        return final_distance


def spell_check(
    word: str,
    dictionary: List[str],
    num_suggestions: int = 10,
    max_edit_distance: int = 3
) -> List[Tuple[str, int]]:
    """
    Provides spelling suggestions for a given word based on a dictionary,
    using the Wagner-Fischer algorithm to calculate edit distance.

    Uses a min-heap for efficiency in finding the top N suggestions.

    Args:
        word: The potentially misspelled word.
        dictionary: A list of correctly spelled words.
        num_suggestions: The maximum number of suggestions to return.
        max_edit_distance: The maximum Levenshtein distance to consider a word
                           as a potential suggestion. Words beyond this distance
                           or with length differences greater than this are ignored.

    Returns:
        A list of tuples, where each tuple contains (suggested_word, distance).
        The list is sorted by distance in ascending order, limited to
        num_suggestions. Returns an empty list if no suggestions are found
        within the max_edit_distance.
    """
    len_word = len(word)
    # Use a min-heap to store the best suggestions found so far.
    # We store (distance, correct_word) tuples. heapq works as a min-heap.
    # To keep the N *smallest* distances, we can push all candidates <= max_edit_distance
    # and then use heapq.nsmallest. Alternatively, maintain a *max-heap* of size N
    # storing (-distance, word) to easily replace the *worst* suggestion (largest distance).
    # Let's use nsmallest for simplicity, it's efficient enough for typical N=10.
    # If D (dictionary size) is truly massive and N is small, a manually managed
    # max-heap might be marginally better.

    candidates = []

    for correct_word in dictionary:
        len_correct = len(correct_word)

        # --- Heuristic Pruning ---
        # 1. Exact match: If the word is in the dictionary, it's likely correct.
        #    (Optional: you might return just the word itself or handle this case separately)
        #    if word == correct_word: return [(word, 0)] # Example: return immediately

        # 2. Length difference heuristic: If lengths differ by more than max_edit_distance,
        #    the edit distance will be at least that large. Skip calculation.
        if abs(len_word - len_correct) > max_edit_distance:
            continue

        # --- Calculate Distance ---
        # Pass max_edit_distance for potential early exit in Wagner-Fischer
        distance = wagner_fischer(word, correct_word, max_distance=max_edit_distance)

        # --- Add Candidate ---
        # Only consider words within the allowed edit distance
        if distance <= max_edit_distance:
             # Use distance as the primary sorting key in the tuple
            candidates.append((distance, correct_word))

    # --- Select Top N ---
    # Find the N smallest distances using heapq.nsmallest
    # It's generally faster than sorting the entire candidates list.
    # The key tells nsmallest how to compare elements (based on distance).
    top_suggestions = heapq.nsmallest(num_suggestions, candidates, key=lambda x: x[0])

    # Return in the desired format (word, distance)
    # nsmallest already sorts them by the key (distance).
    return [(word, dist) for dist, word in top_suggestions]


# === Example Usage ===
if __name__ == "__main__":
    DICTIONARY_FILE = "words.txt" # Make sure this file exists and contains words
    try:
        # Load dictionary only once
        print(f"Loading dictionary from {DICTIONARY_FILE}...")
        dictionary = load_dictionary(DICTIONARY_FILE)
        print(f"Dictionary loaded with {len(dictionary)} words.")

        misspelled_word = "wrlod"
        # Find suggestions with default parameters (N=10, max_distance=3)
        suggestions = spell_check(misspelled_word, dictionary)

        print(f"\nTop suggestions for '{misspelled_word}' (max distance 3):")
        if suggestions:
            for suggested_word, distance in suggestions:
                print(f"- {suggested_word} (Distance: {distance})")
        else:
            print("No suggestions found within the maximum edit distance.")

        # Example with different parameters
        misspelled_word_2 = "recieve"
        suggestions_2 = spell_check(misspelled_word_2, dictionary, num_suggestions=5, max_edit_distance=2)

        print(f"\nTop 5 suggestions for '{misspelled_word_2}' (max distance 2):")
        if suggestions_2:
            for suggested_word, distance in suggestions_2:
                print(f"- {suggested_word} (Distance: {distance})")
        else:
            print("No suggestions found within the maximum edit distance.")

    except FileNotFoundError:
        print("\nPlease ensure 'words.txt' exists in the same directory.")
    except Exception as e:
        print(f"\nAn unexpected error occurred: {e}")