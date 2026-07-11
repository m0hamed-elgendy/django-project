"""
validators.py — Reusable validation functions for the Crowdfunding Platform.

Provides strict validation for emails, Egyptian phone numbers, dates,
positive numbers, non-empty fields, and password confirmation.
Includes form-level validation helpers for registration and project forms.
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


def validate_positive_number(value) -> bool:
    """
    Validate that the given value represents a positive numeric value.

    Rejects negative numbers, zero, and non-numeric input.

    Args:
        value: The value to validate as a positive number.

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


# ------------------------------------------------------------------ #
#  Form-level validation helpers (for web forms)
# ------------------------------------------------------------------ #

def validate_registration_form(data: dict) -> dict:
    """
    Validate all registration form fields at once.

    Args:
        data: Dictionary with keys: first_name, last_name, email,
              password, confirm_password, phone.

    Returns:
        Dictionary of field_name -> error_message for invalid fields.
        Empty dict means all fields are valid.
    """
    errors = {}

    # First name
    valid, msg = validate_non_empty(data.get("first_name", ""), "First name")
    if not valid:
        errors["first_name"] = msg

    # Last name
    valid, msg = validate_non_empty(data.get("last_name", ""), "Last name")
    if not valid:
        errors["last_name"] = msg

    # Email
    email = data.get("email", "").strip()
    if not email:
        errors["email"] = "Email cannot be empty."
    elif not validate_email(email):
        errors["email"] = "Invalid email format."

    # Password
    password = data.get("password", "")
    if not password:
        errors["password"] = "Password cannot be empty."
    elif not validate_password_strength(password):
        errors["password"] = "Password must be at least 6 characters long."

    # Confirm password
    confirm = data.get("confirm_password", "")
    if not confirm:
        errors["confirm_password"] = "Please confirm your password."
    elif not validate_password_match(password, confirm):
        errors["confirm_password"] = "Passwords do not match."

    # Phone
    phone = data.get("phone", "").strip()
    if not phone:
        errors["phone"] = "Phone number cannot be empty."
    elif not validate_egyptian_phone(phone):
        errors["phone"] = (
            "Invalid Egyptian phone number. "
            "Must start with 010, 011, 012, or 015 and be 11 digits."
        )

    return errors


def validate_project_form(data: dict) -> dict:
    """
    Validate all project form fields at once.

    Args:
        data: Dictionary with keys: title, details, total_target,
              start_date, end_date.

    Returns:
        Dictionary of field_name -> error_message for invalid fields.
        Empty dict means all fields are valid.
    """
    errors = {}

    # Title
    valid, msg = validate_non_empty(data.get("title", ""), "Title")
    if not valid:
        errors["title"] = msg

    # Details
    valid, msg = validate_non_empty(data.get("details", ""), "Details")
    if not valid:
        errors["details"] = msg

    # Total target
    target = data.get("total_target", "")
    if not target:
        errors["total_target"] = "Target amount cannot be empty."
    elif not validate_positive_number(target):
        errors["total_target"] = "Target must be a positive number."

    # Start date
    start_date = data.get("start_date", "").strip()
    if not start_date:
        errors["start_date"] = "Start date is required."
    elif not validate_date(start_date):
        errors["start_date"] = "Invalid start date format. Use YYYY-MM-DD."

    # End date
    end_date = data.get("end_date", "").strip()
    if not end_date:
        errors["end_date"] = "End date is required."
    elif not validate_date(end_date):
        errors["end_date"] = "Invalid end date format. Use YYYY-MM-DD."

    # Date range (only if both dates are individually valid)
    if "start_date" not in errors and "end_date" not in errors:
        if start_date and end_date and not validate_date_range(start_date, end_date):
            errors["end_date"] = "End date must be after the start date."

    return errors
