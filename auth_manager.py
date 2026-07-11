"""
auth_manager.py — Authentication manager for the Crowdfunding Platform.

Handles user registration (with activation code generation),
account activation, and login with full validation.
Persists user data to a JSON file. Refactored for web use —
all methods accept data and return result dictionaries (no console I/O).
"""

import json
import os
import random
import string
from models import User
from validators import validate_registration_form


class AuthManager:
    """
    Manages user authentication: registration, activation, and login.

    All user data is persisted to a JSON file so it survives between
    program runs. Methods accept data dictionaries and return result
    dictionaries suitable for use by Flask route handlers.

    Attributes:
        file_path (str): Path to the users JSON file.
        users (list[User]): In-memory list of all registered users.
    """

    def __init__(self, file_path: str = "data/users.json"):
        """
        Initialize the AuthManager and load existing users from disk.

        Args:
            file_path: Path to the JSON file for user persistence.
        """
        self.file_path = file_path
        self.users: list = []
        self.load_users()

    # ------------------------------------------------------------------ #
    #  JSON Persistence
    # ------------------------------------------------------------------ #

    def load_users(self) -> None:
        """Load users from the JSON file into memory."""
        if os.path.exists(self.file_path):
            try:
                with open(self.file_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                self.users = [User.from_dict(u) for u in data]
            except (json.JSONDecodeError, KeyError):
                # File is corrupt or empty — start fresh
                self.users = []
        else:
            self.users = []

    def save_users(self) -> None:
        """Write the current in-memory user list to the JSON file."""
        # Ensure the directory exists
        os.makedirs(os.path.dirname(self.file_path), exist_ok=True)
        with open(self.file_path, "w", encoding="utf-8") as f:
            json.dump([u.to_dict() for u in self.users], f, indent=2)

    # ------------------------------------------------------------------ #
    #  Helpers
    # ------------------------------------------------------------------ #

    def find_user_by_email(self, email: str):
        """
        Look up a user by email (case-insensitive).

        Args:
            email: The email to search for.

        Returns:
            The User object if found, or None.
        """
        email_lower = email.strip().lower()
        for user in self.users:
            if user.email.lower() == email_lower:
                return user
        return None

    @staticmethod
    def _generate_activation_code(length: int = 6) -> str:
        """
        Generate a random alphanumeric activation code.

        Args:
            length: Number of characters in the code (default 6).

        Returns:
            A random string of digits and uppercase letters.
        """
        chars = string.ascii_uppercase + string.digits
        return "".join(random.choices(chars, k=length))

    # ------------------------------------------------------------------ #
    #  Registration
    # ------------------------------------------------------------------ #

    def register(self, data: dict) -> dict:
        """
        Register a new user with validation.

        Args:
            data: Dictionary with keys: first_name, last_name, email,
                  password, confirm_password, phone.

        Returns:
            Dictionary with keys:
                - success (bool): Whether registration succeeded.
                - errors (dict): Field-level error messages (if any).
                - activation_code (str): The generated code (on success).
        """
        # Run field-level validation
        errors = validate_registration_form(data)

        # Check for duplicate email (only if email format is valid)
        email = data.get("email", "").strip().lower()
        if "email" not in errors and self.find_user_by_email(email):
            errors["email"] = "This email is already registered."

        if errors:
            return {"success": False, "errors": errors, "activation_code": ""}

        # Create the user with a hashed password
        code = self._generate_activation_code()
        user = User(
            first_name=data["first_name"].strip(),
            last_name=data["last_name"].strip(),
            email=email,
            password_hash="",  # Will be set by set_password()
            phone=data["phone"].strip(),
            is_active=False,
            activation_code=code,
        )
        user.set_password(data["password"])

        self.users.append(user)
        self.save_users()

        return {
            "success": True,
            "errors": {},
            "activation_code": code,
        }

    # ------------------------------------------------------------------ #
    #  Account Activation
    # ------------------------------------------------------------------ #

    def activate(self, email: str, code: str) -> dict:
        """
        Activate a user account with the given activation code.

        Args:
            email: The user's email address.
            code: The activation code to verify.

        Returns:
            Dictionary with keys:
                - success (bool): Whether activation succeeded.
                - message (str): A user-facing message.
        """
        if not email or not email.strip():
            return {"success": False, "message": "Email is required."}

        if not code or not code.strip():
            return {"success": False, "message": "Activation code is required."}

        user = self.find_user_by_email(email.strip())
        if not user:
            return {"success": False, "message": "No account found with that email."}

        if user.is_active:
            return {"success": False, "message": "This account is already active."}

        if code.strip() != user.activation_code:
            return {"success": False, "message": "Invalid activation code."}

        user.is_active = True
        user.activation_code = ""  # Clear the code after use
        self.save_users()

        return {"success": True, "message": "Account activated successfully! You can now log in."}

    # ------------------------------------------------------------------ #
    #  Login
    # ------------------------------------------------------------------ #

    def login(self, email: str, password: str) -> dict:
        """
        Authenticate a user with email and password.

        Args:
            email: The user's email address.
            password: The plain-text password to verify.

        Returns:
            Dictionary with keys:
                - success (bool): Whether login succeeded.
                - user (User | None): The User object on success, None on failure.
                - message (str): A user-facing message.
        """
        if not email or not email.strip():
            return {"success": False, "user": None, "message": "Email is required."}

        if not password:
            return {"success": False, "user": None, "message": "Password is required."}

        user = self.find_user_by_email(email.strip())

        # Intentionally vague for security, but clear enough for dev/testing
        if not user:
            return {
                "success": False,
                "user": None,
                "message": "Invalid email or password.",
            }

        if not user.check_password(password):
            return {
                "success": False,
                "user": None,
                "message": "Invalid email or password.",
            }

        if not user.is_active:
            return {
                "success": False,
                "user": None,
                "message": "Your account is not activated yet. Please activate your account first.",
            }

        return {
            "success": True,
            "user": user,
            "message": f"Welcome back, {user.first_name}!",
        }
