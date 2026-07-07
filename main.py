"""
main.py — Entry point for the Crowdfunding Platform CLI application.

Provides a menu-driven console interface with two layers:
  1. Pre-login menu: Register, Activate Account, Login, Exit
  2. Post-login menu: Create Project, View All Projects, Edit, Delete,
                      Search by Date, Logout

All input is wrapped in try/except to prevent crashes on bad input.
"""

from auth_manager import AuthManager
from project_manager import ProjectManager


def print_main_menu() -> None:
    """Display the pre-login (guest) menu."""
    print("\n" + "╔" + "═" * 48 + "╗")
    print("║" + "  CROWDFUNDING PLATFORM  ".center(48) + "║")
    print("╠" + "═" * 48 + "╣")
    print("║" + "  [1] Register".ljust(48) + "║")
    print("║" + "  [2] Activate Account".ljust(48) + "║")
    print("║" + "  [3] Login".ljust(48) + "║")
    print("║" + "  [4] Exit".ljust(48) + "║")
    print("╚" + "═" * 48 + "╝")


def print_user_menu(first_name: str) -> None:
    """
    Display the post-login (authenticated) menu.

    Args:
        first_name: The logged-in user's first name for the welcome message.
    """
    welcome = f"  Welcome, {first_name}!"
    print("\n" + "╔" + "═" * 48 + "╗")
    print("║" + welcome.ljust(48) + "║")
    print("╠" + "═" * 48 + "╣")
    print("║" + "  [1] Create Project".ljust(48) + "║")
    print("║" + "  [2] View All Projects".ljust(48) + "║")
    print("║" + "  [3] Edit My Project".ljust(48) + "║")
    print("║" + "  [4] Delete My Project".ljust(48) + "║")
    print("║" + "  [5] Search Projects by Date".ljust(48) + "║")
    print("║" + "  [6] Logout".ljust(48) + "║")
    print("╚" + "═" * 48 + "╝")


def user_menu(user, auth_mgr: AuthManager, proj_mgr: ProjectManager) -> None:
    """
    Run the post-login menu loop.

    Allows the authenticated user to create, view, edit, delete projects
    and search by date. Loops until the user chooses to log out.

    Args:
        user: The logged-in User object.
        auth_mgr: The AuthManager instance (for future use if needed).
        proj_mgr: The ProjectManager instance.
    """
    while True:
        print_user_menu(user.first_name)
        choice = input("  Your choice: ").strip()

        try:
            if choice == "1":
                proj_mgr.create_project(user.email)

            elif choice == "2":
                proj_mgr.view_all_projects()

            elif choice == "3":
                proj_mgr.edit_project(user.email)

            elif choice == "4":
                proj_mgr.delete_project(user.email)

            elif choice == "5":
                proj_mgr.search_by_date()

            elif choice == "6":
                print(f"\n  Goodbye, {user.first_name}! Logged out.\n")
                break

            else:
                print("  ✗ Invalid choice. Please enter a number 1-6.")

        except Exception as e:
            print(f"  ✗ An unexpected error occurred: {e}")


def main() -> None:
    """
    Run the main application loop.

    Initializes the AuthManager and ProjectManager (loading data from
    JSON files), then presents the pre-login menu in a loop.
    """
    auth_mgr = AuthManager("users.json")
    proj_mgr = ProjectManager("projects.json")

    print("\n" + "★" * 50)
    print("   Welcome to the Crowdfunding Platform!")
    print("   Fund your dreams. Support great ideas.")
    print("★" * 50)

    while True:
        print_main_menu()
        choice = input("  Your choice: ").strip()

        try:
            if choice == "1":
                auth_mgr.register()

            elif choice == "2":
                auth_mgr.activate_account()

            elif choice == "3":
                user = auth_mgr.login()
                if user:
                    user_menu(user, auth_mgr, proj_mgr)

            elif choice == "4":
                print("\n  Thank you for using Crowdfunding Platform!")
                print("  Goodbye! 👋\n")
                break

            else:
                print("  ✗ Invalid choice. Please enter a number 1-4.")

        except KeyboardInterrupt:
            print("\n\n  Interrupted. Goodbye!\n")
            break
        except Exception as e:
            print(f"  ✗ An unexpected error occurred: {e}")


if __name__ == "__main__":
    main()
