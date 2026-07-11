"""
models.py — Data models for the Crowdfunding Platform.

Defines the User and Project classes with serialization/deserialization
methods for JSON persistence. User passwords are hashed using werkzeug.
"""

from werkzeug.security import generate_password_hash, check_password_hash


class User:
    """
    Represents a registered user on the crowdfunding platform.

    Attributes:
        first_name (str): User's first name.
        last_name (str): User's last name.
        email (str): User's email address (unique identifier).
        password_hash (str): Hashed password (never stored in plain text).
        phone (str): User's Egyptian mobile phone number.
        is_active (bool): Whether the account has been activated.
        activation_code (str): The code required to activate the account.
    """

    def __init__(self, first_name: str, last_name: str, email: str,
                 password_hash: str, phone: str, is_active: bool = False,
                 activation_code: str = ""):
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.password_hash = password_hash
        self.phone = phone
        self.is_active = is_active
        self.activation_code = activation_code

    def set_password(self, plain_password: str) -> None:
        """
        Hash and store the given plain-text password.

        Args:
            plain_password: The plain-text password to hash.
        """
        self.password_hash = generate_password_hash(plain_password)

    def check_password(self, plain_password: str) -> bool:
        """
        Verify a plain-text password against the stored hash.

        Args:
            plain_password: The plain-text password to verify.

        Returns:
            True if the password matches the stored hash, False otherwise.
        """
        return check_password_hash(self.password_hash, plain_password)

    def to_dict(self) -> dict:
        """Serialize the User instance to a dictionary for JSON storage."""
        return {
            "first_name": self.first_name,
            "last_name": self.last_name,
            "email": self.email,
            "password_hash": self.password_hash,
            "phone": self.phone,
            "is_active": self.is_active,
            "activation_code": self.activation_code,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "User":
        """
        Deserialize a dictionary into a User instance.

        Args:
            data: Dictionary containing user fields.

        Returns:
            A new User instance populated from the dictionary.
        """
        return cls(
            first_name=data["first_name"],
            last_name=data["last_name"],
            email=data["email"],
            password_hash=data.get("password_hash", ""),
            phone=data["phone"],
            is_active=data.get("is_active", False),
            activation_code=data.get("activation_code", ""),
        )

    def __str__(self) -> str:
        status = "Active" if self.is_active else "Inactive"
        return f"{self.first_name} {self.last_name} ({self.email}) [{status}]"


class Project:
    """
    Represents a crowdfunding project/campaign.

    Attributes:
        id (int): Unique project identifier.
        title (str): Project title.
        details (str): Project description/details.
        total_target (float): Fundraising target amount in EGP.
        current_funding (float): Total funds raised so far.
        start_date (str): Project start date (YYYY-MM-DD).
        end_date (str): Project end date (YYYY-MM-DD).
        owner_email (str): Email of the user who created the project.
    """

    def __init__(self, project_id: int, title: str, details: str,
                 total_target: float, start_date: str, end_date: str,
                 owner_email: str, current_funding: float = 0.0):
        self.id = project_id
        self.title = title
        self.details = details
        self.total_target = total_target
        self.current_funding = current_funding
        self.start_date = start_date
        self.end_date = end_date
        self.owner_email = owner_email

    @property
    def percent_funded(self) -> int:
        """Calculate the percentage of the target goal funded so far."""
        if self.total_target <= 0:
            return 0
        return min(int((self.current_funding / self.total_target) * 100), 100)

    def to_dict(self) -> dict:
        """Serialize the Project instance to a dictionary for JSON storage."""
        return {
            "id": self.id,
            "title": self.title,
            "details": self.details,
            "total_target": self.total_target,
            "current_funding": self.current_funding,
            "start_date": self.start_date,
            "end_date": self.end_date,
            "owner_email": self.owner_email,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Project":
        """
        Deserialize a dictionary into a Project instance.

        Args:
            data: Dictionary containing project fields.

        Returns:
            A new Project instance populated from the dictionary.
        """
        return cls(
            project_id=data["id"],
            title=data["title"],
            details=data["details"],
            total_target=data["total_target"],
            start_date=data["start_date"],
            end_date=data["end_date"],
            owner_email=data["owner_email"],
            current_funding=data.get("current_funding", 0.0),
        )

    def __str__(self) -> str:
        return (
            f"  Project #{self.id}\n"
            f"  Title       : {self.title}\n"
            f"  Details     : {self.details}\n"
            f"  Target      : {self.total_target:,.2f} EGP\n"
            f"  Raised      : {self.current_funding:,.2f} EGP ({self.percent_funded}%)\n"
            f"  Start Date  : {self.start_date}\n"
            f"  End Date    : {self.end_date}\n"
            f"  Owner       : {self.owner_email}"
        )
