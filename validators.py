"""
validators.py — Reusable validation functions for the Crowdfunding Platform.

Provides strict validation for emails, Egyptian phone numbers, dates,
positive numbers, non-empty fields, and password confirmation.
"""

import re
from datetime import datetime


def validate_email(email: str) -> bool:
    """
    Validate that the given string is a properly formatted email address.

    Uses a standard regex pattern that checks for:
      - One or more word/dot/hyphen/plus characters before the '@'
      - A domain name with at least one dot
      - A TLD of 2 or more alphabetic characters

    Args:
        email: The email string to validate.

    Returns:
        True if the email matches the pattern, False otherwise.
    """
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email.strip()))


def validate_egyptian_phone(phone: str) -> bool:
    """
    Validate that the given string is a valid Egyptian mobile phone number.

    Egyptian mobile numbers must:
      - Start with 010, 011, 012, or 015
      - Be followed by exactly 8 more digits
      - Total length: 11 digits

    Args:
        phone: The phone number string to validate.

    Returns:
        True if valid, False otherwise.
    """
    pattern = r'^01[0125]\d{8}$'
    return bool(re.match(pattern, phone.strip()))


def validate_date(date_str: str) -> bool:
    """
    Validate that the given string is a valid date in YYYY-MM-DD format.

    Uses datetime.strptime with proper error handling to reject
    invalid calendar dates (e.g., 2024-02-30).

    Args:
        date_str: The date string to validate.

    Returns:
        True if the date is valid, False otherwise.
    """
    try:
        datetime.strptime(date_str.strip(), '%Y-%m-%d')
        return True
    except ValueError:
        return False


def parse_date(date_str: str) -> datetime:
    """
    Parse a YYYY-MM-DD date string into a datetime object.

    Args:
        date_str: The date string to parse (must be valid YYYY-MM-DD).

    Returns:
        A datetime object representing the date.

    Raises:
        ValueError: If the date string is not valid.
    """
    return datetime.strptime(date_str.strip(), '%Y-%m-%d')


def validate_date_range(start_date_str: str, end_date_str: str) -> bool:
    """
    Validate that the end date is strictly after the start date.

    Both dates must already be valid YYYY-MM-DD strings.

    Args:
        start_date_str: The start date string.
        end_date_str: The end date string.

    Returns:
        True if end_date > start_date, False otherwise.
    """
    try:
        start = parse_date(start_date_str)
        end = parse_date(end_date_str)
        return end > start
    except ValueError:
        return False


def validate_positive_number(value: str) -> bool:
    """
    Validate that the given string represents a positive numeric value.

    Rejects negative numbers, zero, and non-numeric input.

    Args:
        value: The string to validate as a positive number.

    Returns:
        True if the value is a positive number, False otherwise.
    """
    try:
        num = float(value)
        return num > 0
    except (ValueError, TypeError):
        return False


def validate_non_empty(value: str, field_name: str = "Field") -> tuple:
    """
    Validate that the given string is not empty after stripping whitespace.

    Args:
        value: The string to validate.
        field_name: The name of the field (for error messages).

    Returns:
        A tuple of (is_valid: bool, error_message: str).
        error_message is empty if valid.
    """
    if not value or not value.strip():
        return False, f"{field_name} cannot be empty."
    return True, ""


def validate_password_match(password: str, confirm_password: str) -> bool:
    """
    Validate that the password and confirmation password match exactly.

    Args:
        password: The original password.
        confirm_password: The confirmation password.

    Returns:
        True if they match exactly, False otherwise.
    """
    return password == confirm_password


def validate_password_strength(password: str, min_length: int = 6) -> bool:
    """
    Validate that the password meets minimum length requirements.

    Args:
        password: The password string to check.
        min_length: Minimum acceptable length (default: 6).

    Returns:
        True if the password meets the minimum length, False otherwise.
    """
    return len(password.strip()) >= min_length
