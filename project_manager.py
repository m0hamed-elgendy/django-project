"""
project_manager.py — Project (campaign) manager for the Crowdfunding Platform.

Handles creating, viewing, editing, deleting, and searching
crowdfunding projects. Persists project data to a JSON file.
Refactored for web use — all methods accept data and return
result dictionaries (no console I/O).
"""

import json
import os
from models import Project
from validators import validate_project_form, validate_date, parse_date


class ProjectManager:
    """
    Manages crowdfunding projects: CRUD operations and search.

    All project data is persisted to a JSON file so it survives
    between program runs. Methods accept data dictionaries and return
    result dictionaries suitable for use by Flask route handlers.

    Attributes:
        file_path (str): Path to the projects JSON file.
        projects (list[Project]): In-memory list of all projects.
    """

    def __init__(self, file_path: str = "data/projects.json"):
        """
        Initialize the ProjectManager and load existing projects from disk.

        Args:
            file_path: Path to the JSON file for project persistence.
        """
        self.file_path = file_path
        self.projects: list = []
        self.load_projects()

    # ------------------------------------------------------------------ #
    #  JSON Persistence
    # ------------------------------------------------------------------ #

    def load_projects(self) -> None:
        """Load projects from the JSON file into memory."""
        if os.path.exists(self.file_path):
            try:
                with open(self.file_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                self.projects = [Project.from_dict(p) for p in data]
            except (json.JSONDecodeError, KeyError):
                self.projects = []
        else:
            self.projects = []

    def save_projects(self) -> None:
        """Write the current in-memory project list to the JSON file."""
        os.makedirs(os.path.dirname(self.file_path), exist_ok=True)
        with open(self.file_path, "w", encoding="utf-8") as f:
            json.dump([p.to_dict() for p in self.projects], f, indent=2)

    # ------------------------------------------------------------------ #
    #  Helpers
    # ------------------------------------------------------------------ #

    def _next_id(self) -> int:
        """Generate the next unique project ID."""
        if not self.projects:
            return 1
        return max(p.id for p in self.projects) + 1

    def get_project_by_id(self, project_id: int):
        """
        Find a project by its ID.

        Args:
            project_id: The unique project identifier.

        Returns:
            The Project object if found, or None.
        """
        for project in self.projects:
            if project.id == project_id:
                return project
        return None

    # ------------------------------------------------------------------ #
    #  Create Project
    # ------------------------------------------------------------------ #

    def create_project(self, data: dict, owner_email: str) -> dict:
        """
        Create a new project with validation.

        Args:
            data: Dictionary with keys: title, details, total_target,
                  start_date, end_date.
            owner_email: The email of the logged-in user creating the project.

        Returns:
            Dictionary with keys:
                - success (bool): Whether creation succeeded.
                - errors (dict): Field-level error messages (if any).
                - project (Project | None): The created project on success.
        """
        errors = validate_project_form(data)

        if errors:
            return {"success": False, "errors": errors, "project": None}

        project = Project(
            project_id=self._next_id(),
            title=data["title"].strip(),
            details=data["details"].strip(),
            total_target=float(data["total_target"]),
            start_date=data["start_date"].strip(),
            end_date=data["end_date"].strip(),
            owner_email=owner_email,
        )
        self.projects.append(project)
        self.save_projects()

        return {"success": True, "errors": {}, "project": project}

    # ------------------------------------------------------------------ #
    #  View All Projects
    # ------------------------------------------------------------------ #

    def get_all_projects(self) -> list:
        """
        Return all projects from all users.

        Returns:
            List of all Project objects.
        """
        return self.projects

    # ------------------------------------------------------------------ #
    #  Update Project (owner-only)
    # ------------------------------------------------------------------ #

    def update_project(self, project_id: int, data: dict, owner_email: str) -> dict:
        """
        Update an existing project with validation.

        Only the project owner can update it.

        Args:
            project_id: The ID of the project to update.
            data: Dictionary with keys: title, details, total_target,
                  start_date, end_date.
            owner_email: Email of the currently logged-in user.

        Returns:
            Dictionary with keys:
                - success (bool): Whether the update succeeded.
                - errors (dict): Field-level error messages (if any).
                - forbidden (bool): True if the user is not the owner.
                - not_found (bool): True if the project doesn't exist.
        """
        project = self.get_project_by_id(project_id)

        if not project:
            return {
                "success": False,
                "errors": {},
                "forbidden": False,
                "not_found": True,
            }

        if project.owner_email != owner_email:
            return {
                "success": False,
                "errors": {},
                "forbidden": True,
                "not_found": False,
            }

        errors = validate_project_form(data)

        if errors:
            return {
                "success": False,
                "errors": errors,
                "forbidden": False,
                "not_found": False,
            }

        # Update the project fields
        project.title = data["title"].strip()
        project.details = data["details"].strip()
        project.total_target = float(data["total_target"])
        project.start_date = data["start_date"].strip()
        project.end_date = data["end_date"].strip()

        self.save_projects()

        return {
            "success": True,
            "errors": {},
            "forbidden": False,
            "not_found": False,
        }

    # ------------------------------------------------------------------ #
    #  Delete Project (owner-only)
    # ------------------------------------------------------------------ #

    def delete_project(self, project_id: int, owner_email: str) -> dict:
        """
        Delete a project by its ID.

        Only the project owner can delete it.

        Args:
            project_id: The ID of the project to delete.
            owner_email: Email of the currently logged-in user.

        Returns:
            Dictionary with keys:
                - success (bool): Whether deletion succeeded.
                - forbidden (bool): True if the user is not the owner.
                - not_found (bool): True if the project doesn't exist.
                - message (str): A user-facing message.
        """
        project = self.get_project_by_id(project_id)

        if not project:
            return {
                "success": False,
                "forbidden": False,
                "not_found": True,
                "message": "Project not found.",
            }

        if project.owner_email != owner_email:
            return {
                "success": False,
                "forbidden": True,
                "not_found": False,
                "message": "Permission denied. You can only delete your own projects.",
            }

        self.projects.remove(project)
        self.save_projects()

        return {
            "success": True,
            "forbidden": False,
            "not_found": False,
            "message": f"Project '{project.title}' deleted successfully!",
        }

    # ------------------------------------------------------------------ #
    #  Search by Date (BONUS)
    # ------------------------------------------------------------------ #

    def search_by_date(self, start_date_str: str, end_date_str: str = "") -> list:
        """
        Search for projects by date or date range.

        If only start_date is given, finds projects active on that date
        (project.start_date <= date <= project.end_date).

        If both dates are given, finds projects that overlap with the range.

        Args:
            start_date_str: The start date (or single date) in YYYY-MM-DD.
            end_date_str: Optional end date in YYYY-MM-DD for range search.

        Returns:
            List of matching Project objects.
        """
        if not validate_date(start_date_str):
            return []

        if end_date_str and not validate_date(end_date_str):
            return []

        search_start = parse_date(start_date_str)

        if end_date_str:
            search_end = parse_date(end_date_str)
            # Projects that overlap with the search range
            return [
                p for p in self.projects
                if parse_date(p.start_date) <= search_end
                and parse_date(p.end_date) >= search_start
            ]
        else:
            # Single date: projects active on that date
            return [
                p for p in self.projects
                if parse_date(p.start_date) <= search_start <= parse_date(p.end_date)
            ]
