import math
import re

def calculate_read_time(content: str) -> int:
    """Calculate estimated read time in minutes based on content"""
    # Remove HTML tags
    text = re.sub(r'<[^>]+>', '', content)
    
    # Split by whitespace and count words
    words = text.split()
    word_count = len(words)

    # Calculate read time (round up)
    read_time = max(1, math.ceil(word_count / 200))
    return read_time
