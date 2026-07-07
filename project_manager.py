"""
project_manager.py — Project (campaign) manager for the Crowdfunding Platform.

Handles creating, viewing, editing, deleting, and searching
crowdfunding projects. Persists project data to a JSON file.
"""

import json
import os
from models import Project
from validators import (
    validate_non_empty,
    validate_positive_number,
    validate_date,
    validate_date_range,
    parse_date,
)


class ProjectManager:
    """
    Manages crowdfunding projects: CRUD operations and search.

    All project data is persisted to a JSON file so it survives
    between program runs.

    Attributes:
        file_path (str): Path to the projects JSON file.
        projects (list[Project]): In-memory list of all projects.
    """

    def __init__(self, file_path: str = "projects.json"):
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

    def _find_project_by_id(self, project_id: int):
        """
        Find a project by its ID.

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

    def create_project(self, owner_email: str) -> bool:
        """
        Interactive project creation flow.

        Collects and validates: title, details, total target amount,
        start date, and end date. Links the project to the owner's email.

        Args:
            owner_email: The email of the logged-in user creating the project.

        Returns:
            True if the project was created successfully, False otherwise.
        """
        print("\n" + "=" * 50)
        print("        CREATE NEW PROJECT")
        print("=" * 50)

        # --- Title ---
        title = input("  Title        : ").strip()
        valid, msg = validate_non_empty(title, "Title")
        if not valid:
            print(f"  ✗ {msg}")
            return False

        # --- Details ---
        details = input("  Details      : ").strip()
        valid, msg = validate_non_empty(details, "Details")
        if not valid:
            print(f"  ✗ {msg}")
            return False

        # --- Total Target ---
        target_str = input("  Target (EGP) : ").strip()
        if not validate_positive_number(target_str):
            print("  ✗ Target must be a positive number.")
            return False
        total_target = float(target_str)

        # --- Start Date ---
        start_date = input("  Start date (YYYY-MM-DD) : ").strip()
        if not validate_date(start_date):
            print("  ✗ Invalid date format. Use YYYY-MM-DD.")
            return False

        # --- End Date ---
        end_date = input("  End date   (YYYY-MM-DD) : ").strip()
        if not validate_date(end_date):
            print("  ✗ Invalid date format. Use YYYY-MM-DD.")
            return False

        if not validate_date_range(start_date, end_date):
            print("  ✗ End date must be after the start date.")
            return False

        # --- Create ---
        project = Project(
            project_id=self._next_id(),
            title=title,
            details=details,
            total_target=total_target,
            start_date=start_date,
            end_date=end_date,
            owner_email=owner_email,
        )
        self.projects.append(project)
        self.save_projects()

        print(f"\n  ✓ Project '{title}' created successfully! (ID: {project.id})\n")
        return True

    # ------------------------------------------------------------------ #
    #  View All Projects
    # ------------------------------------------------------------------ #

    def view_all_projects(self) -> None:
        """
        Display all projects from all users in a formatted list.

        If no projects exist, prints an informative message.
        """
        print("\n" + "=" * 50)
        print("         ALL PROJECTS")
        print("=" * 50)

        if not self.projects:
            print("  No projects found.\n")
            return

        for i, project in enumerate(self.projects):
            print(f"\n  {'─' * 44}")
            print(project)

        print(f"\n  {'─' * 44}")
        print(f"  Total: {len(self.projects)} project(s)\n")

    # ------------------------------------------------------------------ #
    #  Edit Project (owner-only)
    # ------------------------------------------------------------------ #

    def edit_project(self, owner_email: str) -> bool:
        """
        Interactive project editing flow (owner-only).

        Lists the user's projects, asks which one to edit,
        then allows updating any field with the same validation rules.
        Press Enter on any field to keep the current value.

        Args:
            owner_email: Email of the currently logged-in user.

        Returns:
            True if a project was edited successfully, False otherwise.
        """
        print("\n" + "=" * 50)
        print("         EDIT PROJECT")
        print("=" * 50)

        # Show user's own projects
        my_projects = [p for p in self.projects if p.owner_email == owner_email]
        if not my_projects:
            print("  You have no projects to edit.\n")
            return False

        print("  Your projects:")
        for p in my_projects:
            print(f"    [{p.id}] {p.title}")

        # Select project
        try:
            pid = int(input("\n  Enter project ID to edit: ").strip())
        except ValueError:
            print("  ✗ Invalid project ID.")
            return False

        project = self._find_project_by_id(pid)
        if not project:
            print("  ✗ Project not found.")
            return False

        if project.owner_email != owner_email:
            print("  ✗ Permission denied! You can only edit your own projects.")
            return False

        print(f"\n  Editing project '{project.title}'")
        print("  (Press Enter to keep current value)\n")

        # --- Title ---
        new_title = input(f"  Title [{project.title}] : ").strip()
        if new_title:
            valid, msg = validate_non_empty(new_title, "Title")
            if not valid:
                print(f"  ✗ {msg}")
                return False
            project.title = new_title

        # --- Details ---
        new_details = input(f"  Details [{project.details}] : ").strip()
        if new_details:
            valid, msg = validate_non_empty(new_details, "Details")
            if not valid:
                print(f"  ✗ {msg}")
                return False
            project.details = new_details

        # --- Total Target ---
        new_target = input(f"  Target (EGP) [{project.total_target}] : ").strip()
        if new_target:
            if not validate_positive_number(new_target):
                print("  ✗ Target must be a positive number.")
                return False
            project.total_target = float(new_target)

        # --- Start Date ---
        new_start = input(f"  Start date [{project.start_date}] : ").strip()
        if new_start:
            if not validate_date(new_start):
                print("  ✗ Invalid date format. Use YYYY-MM-DD.")
                return False
            project.start_date = new_start

        # --- End Date ---
        new_end = input(f"  End date [{project.end_date}] : ").strip()
        if new_end:
            if not validate_date(new_end):
                print("  ✗ Invalid date format. Use YYYY-MM-DD.")
                return False
            project.end_date = new_end

        # --- Validate date range after all edits ---
        if not validate_date_range(project.start_date, project.end_date):
            print("  ✗ End date must be after the start date.")
            return False

        self.save_projects()
        print(f"\n  ✓ Project '{project.title}' updated successfully!\n")
        return True

    # ------------------------------------------------------------------ #
    #  Delete Project (owner-only)
    # ------------------------------------------------------------------ #

    def delete_project(self, owner_email: str) -> bool:
        """
        Interactive project deletion flow (owner-only).

        Lists the user's projects, asks which one to delete,
        and confirms before removing it.

        Args:
            owner_email: Email of the currently logged-in user.

        Returns:
            True if a project was deleted successfully, False otherwise.
        """
        print("\n" + "=" * 50)
        print("        DELETE PROJECT")
        print("=" * 50)

        # Show user's own projects
        my_projects = [p for p in self.projects if p.owner_email == owner_email]
        if not my_projects:
            print("  You have no projects to delete.\n")
            return False

        print("  Your projects:")
        for p in my_projects:
            print(f"    [{p.id}] {p.title}")

        # Select project
        try:
            pid = int(input("\n  Enter project ID to delete: ").strip())
        except ValueError:
            print("  ✗ Invalid project ID.")
            return False

        project = self._find_project_by_id(pid)
        if not project:
            print("  ✗ Project not found.")
            return False

        if project.owner_email != owner_email:
            print("  ✗ Permission denied! You can only delete your own projects.")
            return False

        # Confirmation
        confirm = input(
            f"  Are you sure you want to delete '{project.title}'? (yes/no): "
        ).strip().lower()
        if confirm not in ("yes", "y"):
            print("  Deletion cancelled.\n")
            return False

        self.projects.remove(project)
        self.save_projects()

        print(f"\n  ✓ Project '{project.title}' deleted successfully!\n")
        return True

    # ------------------------------------------------------------------ #
    #  Search by Date (BONUS)
    # ------------------------------------------------------------------ #

    def search_by_date(self) -> None:
        """
        Interactive search for projects by date or date range.

        The user can enter:
          - A single date to find projects active on that date
            (start_date <= date <= end_date)
          - A date range (start and end) to find projects that overlap
            with the given range

        Results are displayed in a formatted list.
        """
        print("\n" + "=" * 50)
        print("       SEARCH PROJECTS BY DATE")
        print("=" * 50)
        print("  [1] Search by a single date")
        print("  [2] Search by a date range")

        choice = input("\n  Your choice: ").strip()

        if choice == "1":
            date_str = input("  Enter date (YYYY-MM-DD): ").strip()
            if not validate_date(date_str):
                print("  ✗ Invalid date format. Use YYYY-MM-DD.")
                return

            search_date = parse_date(date_str)
            results = [
                p for p in self.projects
                if parse_date(p.start_date) <= search_date <= parse_date(p.end_date)
            ]

        elif choice == "2":
            start_str = input("  Range start (YYYY-MM-DD): ").strip()
            if not validate_date(start_str):
                print("  ✗ Invalid start date. Use YYYY-MM-DD.")
                return

            end_str = input("  Range end   (YYYY-MM-DD): ").strip()
            if not validate_date(end_str):
                print("  ✗ Invalid end date. Use YYYY-MM-DD.")
                return

            if not validate_date_range(start_str, end_str):
                print("  ✗ Range end must be after range start.")
                return

            range_start = parse_date(start_str)
            range_end = parse_date(end_str)

            # Projects that overlap with the search range
            results = [
                p for p in self.projects
                if parse_date(p.start_date) <= range_end
                and parse_date(p.end_date) >= range_start
            ]
        else:
            print("  ✗ Invalid choice.")
            return

        # Display results
        if not results:
            print("  No projects found matching your search.\n")
            return

        print(f"\n  Found {len(results)} project(s):")
        for project in results:
            print(f"\n  {'─' * 44}")
            print(project)
        print(f"\n  {'─' * 44}\n")
