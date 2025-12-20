"""
Utility functions for TalentScout
"""
import re

def validate_email(email):
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email.strip()) is not None

def validate_phone(phone):
    """Validate phone number"""
    digits = re.sub(r'\D', '', phone)
    return len(digits) >= 10

def check_exit(text):
    """Check if user wants to exit"""
    exit_words = ["exit", "quit", "bye", "goodbye", "stop", "end", "cancel"]
    return text.lower().strip() in exit_words
