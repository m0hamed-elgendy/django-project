"""
auth_manager.py — Authentication manager for the Crowdfunding Platform.

Handles user registration (with activation code generation),
account activation, and login with full validation.
Persists user data to a JSON file.
"""

import json
import os
import random
import string
from models import User
from validators import (
    validate_email,
    validate_egyptian_phone,
    validate_non_empty,
    validate_password_match,
    validate_password_strength,
)


class AuthManager:
    """
    Manages user authentication: registration, activation, and login.

    All user data is persisted to a JSON file so it survives between
    program runs.

    Attributes:
        file_path (str): Path to the users JSON file.
        users (list[User]): In-memory list of all registered users.
    """

    def __init__(self, file_path: str = "users.json"):
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
        with open(self.file_path, "w", encoding="utf-8") as f:
            json.dump([u.to_dict() for u in self.users], f, indent=2)

    # ------------------------------------------------------------------ #
    #  Helpers
    # ------------------------------------------------------------------ #

    def _find_user_by_email(self, email: str):
        """
        Look up a user by email (case-insensitive).

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

    def register(self) -> bool:
        """
        Interactive registration flow.

        Collects and validates: first name, last name, email (unique),
        password + confirmation, and Egyptian phone number.
        Creates an inactive account and prints the activation code.

        Returns:
            True if registration succeeded, False otherwise.
        """
        print("\n" + "=" * 50)
        print("         USER REGISTRATION")
        print("=" * 50)

        # --- First name ---
        first_name = input("  First name : ").strip()
        valid, msg = validate_non_empty(first_name, "First name")
        if not valid:
            print(f"  ✗ {msg}")
            return False

        # --- Last name ---
        last_name = input("  Last name  : ").strip()
        valid, msg = validate_non_empty(last_name, "Last name")
        if not valid:
            print(f"  ✗ {msg}")
            return False

        # --- Email ---
        email = input("  Email      : ").strip()
        if not validate_email(email):
            print("  ✗ Invalid email format.")
            return False
        if self._find_user_by_email(email):
            print("  ✗ This email is already registered.")
            return False

        # --- Password ---
        password = input("  Password   : ").strip()
        if not validate_password_strength(password):
            print("  ✗ Password must be at least 6 characters long.")
            return False

        confirm = input("  Confirm PW : ").strip()
        if not validate_password_match(password, confirm):
            print("  ✗ Passwords do not match.")
            return False

        # --- Phone ---
        phone = input("  Phone      : ").strip()
        if not validate_egyptian_phone(phone):
            print("  ✗ Invalid Egyptian phone number.")
            print("    Must start with 010, 011, 012, or 015 and be 11 digits.")
            return False

        # --- Create the user ---
        code = self._generate_activation_code()
        user = User(
            first_name=first_name,
            last_name=last_name,
            email=email.lower(),
            password=password,
            phone=phone,
            is_active=False,
            activation_code=code,
        )
        self.users.append(user)
        self.save_users()

        print("\n  ✓ Registration successful!")
        print(f"  ✉ Your activation code is: {code}")
        print("    (Use 'Activate Account' from the main menu.)\n")
        return True

    # ------------------------------------------------------------------ #
    #  Account Activation
    # ------------------------------------------------------------------ #

    def activate_account(self) -> bool:
        """
        Interactive account activation flow.

        Asks for the user's email and the activation code that was
        displayed at registration time.

        Returns:
            True if activation succeeded, False otherwise.
        """
        print("\n" + "=" * 50)
        print("       ACCOUNT ACTIVATION")
        print("=" * 50)

        email = input("  Email           : ").strip()
        user = self._find_user_by_email(email)
        if not user:
            print("  ✗ No account found with that email.")
            return False

        if user.is_active:
            print("  ✗ This account is already active.")
            return False

        code = input("  Activation code : ").strip()
        if code != user.activation_code:
            print("  ✗ Invalid activation code.")
            return False

        user.is_active = True
        user.activation_code = ""  # Clear the code after use
        self.save_users()

        print("  ✓ Account activated successfully! You can now log in.\n")
        return True

    # ------------------------------------------------------------------ #
    #  Login
    # ------------------------------------------------------------------ #

    def login(self):
        """
        Interactive login flow.

        Validates email existence, password match, and active status.

        Returns:
            The User object on successful login, or None on failure.
        """
        print("\n" + "=" * 50)
        print("            USER LOGIN")
        print("=" * 50)

        email = input("  Email    : ").strip()
        user = self._find_user_by_email(email)
        if not user:
            print("  ✗ No account found with that email.")
            return None

        password = input("  Password : ").strip()
        if password != user.password:
            print("  ✗ Incorrect password.")
            return None

        if not user.is_active:
            print("  ✗ Your account is not activated yet.")
            print("    Please activate your account first.")
            return None

        print(f"\n  ✓ Welcome back, {user.first_name}!\n")
        return user
