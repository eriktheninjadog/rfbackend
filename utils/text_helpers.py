"""Text processing utilities"""


def remove_repeating_sentences(text):
    """Remove duplicate sentences from text"""
    sentences = text.split('. ')  # Split text into sentences
    unique_sentences = []

    for sentence in sentences:
        if sentence not in unique_sentences:
            unique_sentences.append(sentence)

    return '. '.join(unique_sentences)