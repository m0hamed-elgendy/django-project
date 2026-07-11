"""
app.py — Flask application for the Crowdfunding Platform.

Entry point for the web application. Defines all routes for authentication
(register, activate, login, logout) and project management (CRUD, search).
Uses Flask sessions for authentication and Jinja2 templates for rendering.
"""

import os
from functools import wraps
from flask import (
    Flask, render_template, request, redirect, url_for,
    session, flash, abort
)
from auth_manager import AuthManager
from project_manager import ProjectManager

# ------------------------------------------------------------------ #
#  App Configuration
# ------------------------------------------------------------------ #

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "crowdfunding-secret-key-change-in-production")

# Initialize managers
auth_mgr = AuthManager("data/users.json")
proj_mgr = ProjectManager("data/projects.json")


# ------------------------------------------------------------------ #
#  Login Required Decorator
# ------------------------------------------------------------------ #

def login_required(f):
    """
    Decorator that ensures a route is only accessible to logged-in users.
    Redirects to the login page if no valid session exists.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user_email" not in session:
            flash("Please log in to access this page.", "warning")
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated_function


# ------------------------------------------------------------------ #
#  Error Handlers
# ------------------------------------------------------------------ #

@app.errorhandler(404)
def page_not_found(e):
    """Custom 404 error page."""
    return render_template("404.html"), 404


@app.errorhandler(403)
def forbidden(e):
    """Custom 403 error page."""
    return render_template("403.html"), 403


# ------------------------------------------------------------------ #
#  Auth Routes
# ------------------------------------------------------------------ #

@app.route("/")
def index():
    """Redirect root to dashboard if logged in, otherwise to login."""
    if "user_email" in session:
        return redirect(url_for("dashboard"))
    return redirect(url_for("login"))


@app.route("/register", methods=["GET", "POST"])
def register():
    """Registration page with form validation."""
    if request.method == "POST":
        data = {
            "first_name": request.form.get("first_name", ""),
            "last_name": request.form.get("last_name", ""),
            "email": request.form.get("email", ""),
            "password": request.form.get("password", ""),
            "confirm_password": request.form.get("confirm_password", ""),
            "phone": request.form.get("phone", ""),
        }

        result = auth_mgr.register(data)

        if result["success"]:
            flash(
                f"Registration successful! Your activation code is: {result['activation_code']}",
                "success"
            )
            return redirect(url_for("activate"))
        else:
            return render_template("register.html", errors=result["errors"], data=data)

    return render_template("register.html", errors={}, data={})


@app.route("/activate", methods=["GET", "POST"])
def activate():
    """Account activation page."""
    if request.method == "POST":
        email = request.form.get("email", "")
        code = request.form.get("activation_code", "")

        result = auth_mgr.activate(email, code)

        if result["success"]:
            flash(result["message"], "success")
            return redirect(url_for("login"))
        else:
            flash(result["message"], "error")
            return render_template("activate.html", email=email)

    return render_template("activate.html", email="")


@app.route("/login", methods=["GET", "POST"])
def login():
    """Login page with session management."""
    if request.method == "POST":
        email = request.form.get("email", "")
        password = request.form.get("password", "")

        result = auth_mgr.login(email, password)

        if result["success"]:
            user = result["user"]
            session["user_email"] = user.email
            session["user_first_name"] = user.first_name
            session["user_last_name"] = user.last_name
            flash(result["message"], "success")
            return redirect(url_for("dashboard"))
        else:
            flash(result["message"], "error")
            return render_template("login.html", email=email)

    return render_template("login.html", email="")


@app.route("/logout")
def logout():
    """Clear the session and redirect to login."""
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for("login"))


# ------------------------------------------------------------------ #
#  Dashboard
# ------------------------------------------------------------------ #

@app.route("/dashboard")
@login_required
def dashboard():
    """Dashboard / home page for logged-in users."""
    return render_template(
        "dashboard.html",
        first_name=session.get("user_first_name", "User"),
    )


# ------------------------------------------------------------------ #
#  Project Routes
# ------------------------------------------------------------------ #

@app.route("/projects")
@login_required
def projects_list():
    """View all projects from all users."""
    projects = proj_mgr.get_all_projects()
    # Look up owner names for display
    enriched = []
    for p in projects:
        owner = auth_mgr.find_user_by_email(p.owner_email)
        owner_name = f"{owner.first_name} {owner.last_name}" if owner else p.owner_email
        enriched.append({"project": p, "owner_name": owner_name})

    return render_template(
        "projects_list.html",
        projects=enriched,
        current_user_email=session.get("user_email"),
    )


@app.route("/projects/create", methods=["GET", "POST"])
@login_required
def project_create():
    """Create a new project."""
    if request.method == "POST":
        data = {
            "title": request.form.get("title", ""),
            "details": request.form.get("details", ""),
            "total_target": request.form.get("total_target", ""),
            "start_date": request.form.get("start_date", ""),
            "end_date": request.form.get("end_date", ""),
        }

        result = proj_mgr.create_project(data, session["user_email"])

        if result["success"]:
            flash(f"Project '{result['project'].title}' created successfully!", "success")
            return redirect(url_for("projects_list"))
        else:
            return render_template("project_create.html", errors=result["errors"], data=data)

    return render_template("project_create.html", errors={}, data={})


@app.route("/projects/edit/<int:project_id>", methods=["GET", "POST"])
@login_required
def project_edit(project_id):
    """Edit an existing project (owner-only)."""
    project = proj_mgr.get_project_by_id(project_id)

    if not project:
        abort(404)

    # Ownership check
    if project.owner_email != session.get("user_email"):
        return render_template("403.html"), 403

    if request.method == "POST":
        data = {
            "title": request.form.get("title", ""),
            "details": request.form.get("details", ""),
            "total_target": request.form.get("total_target", ""),
            "start_date": request.form.get("start_date", ""),
            "end_date": request.form.get("end_date", ""),
        }

        result = proj_mgr.update_project(project_id, data, session["user_email"])

        if result["success"]:
            flash("Project updated successfully!", "success")
            return redirect(url_for("projects_list"))
        elif result.get("forbidden"):
            return render_template("403.html"), 403
        elif result.get("not_found"):
            abort(404)
        else:
            return render_template(
                "project_edit.html",
                project=project,
                errors=result["errors"],
                data=data,
            )

    # GET — pre-fill form with current project data
    data = {
        "title": project.title,
        "details": project.details,
        "total_target": project.total_target,
        "start_date": project.start_date,
        "end_date": project.end_date,
    }
    return render_template("project_edit.html", project=project, errors={}, data=data)


@app.route("/projects/delete/<int:project_id>", methods=["GET", "POST"])
@login_required
def project_delete(project_id):
    """Delete a project (owner-only) with confirmation."""
    project = proj_mgr.get_project_by_id(project_id)

    if not project:
        abort(404)

    # Ownership check
    if project.owner_email != session.get("user_email"):
        return render_template("403.html"), 403

    if request.method == "POST":
        result = proj_mgr.delete_project(project_id, session["user_email"])

        if result["success"]:
            flash(result["message"], "success")
            return redirect(url_for("projects_list"))
        elif result.get("forbidden"):
            return render_template("403.html"), 403
        elif result.get("not_found"):
            abort(404)

    return render_template("project_delete.html", project=project)


@app.route("/projects/search", methods=["GET", "POST"])
@login_required
def project_search():
    """Search projects by date range."""
    results = None

    if request.method == "POST":
        start_date = request.form.get("start_date", "").strip()
        end_date = request.form.get("end_date", "").strip()

        if not start_date:
            flash("Please provide a start date.", "error")
        else:
            results = proj_mgr.search_by_date(start_date, end_date)

            # Enrich with owner names
            enriched = []
            for p in results:
                owner = auth_mgr.find_user_by_email(p.owner_email)
                owner_name = f"{owner.first_name} {owner.last_name}" if owner else p.owner_email
                enriched.append({"project": p, "owner_name": owner_name})
            results = enriched

    return render_template(
        "project_search.html",
        results=results,
        current_user_email=session.get("user_email"),
    )


# ------------------------------------------------------------------ #
#  Run the App
# ------------------------------------------------------------------ #

if __name__ == "__main__":
    app.run(debug=True, port=5000)
