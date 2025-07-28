def load_bad_words(file_path='blocked_words.txt'):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            bad_words = set(line.strip().lower() for line in f if line.strip())
        return bad_words
    except FileNotFoundError:
        print("Error: blocked_words.txt file not found!")
        return set()

def contains_bad_word(text, bad_words):
    text = text.lower()
    for word in bad_words:
        if word in text:
            return True
    return False
