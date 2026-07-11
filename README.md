# 🚀 CrowdFund Platform — Web Application

A **web-based crowdfunding platform** built with Python Flask, inspired by platforms like Kickstarter and GoFundMe. Users can register, activate their accounts, log in, and manage fundraising campaigns (projects) through a modern browser-based UI.

---

## ✨ Features

### Authentication System
- **Registration** with full validation (name, email, phone, password)
- **Account Activation** via a generated activation code (displayed on-screen)
- **Login/Logout** with Flask session management
- **Password Hashing** using `werkzeug.security` (never stored in plain text)

### Project Management (CRUD)
- **Create** new crowdfunding projects linked to your account
- **View** all projects from all users in a card-based layout
- **Edit** your own projects (owner-only, with server-side permission checks)
- **Delete** your own projects (owner-only, with confirmation page)
- **Search** projects by a specific date or date range (bonus feature)

### Validation (Client + Server)
- Email format validation (regex — both client-side JS and server-side Python)
- Egyptian mobile phone validation (010/011/012/015 + 8 digits = 11 digits)
- Date format and logic validation (end date must be after start date)
- Positive number validation for target amounts
- Password confirmation matching and minimum length
- Non-empty field checks for all required inputs

### UI/UX Design
- Modern, responsive design with Inter font and teal/blue color palette
- Card-based layouts with subtle shadows and micro-animations
- Flash message system for success/error/warning feedback
- Consistent navbar across all authenticated pages
- Mobile-friendly responsive breakpoints
- Custom 404 and 403 error pages

### Data Persistence
- All data saved to **JSON files** (`data/users.json`, `data/projects.json`)
- Data persists between server restarts

---

## 🛠️ Tech Stack

| Layer       | Technology                          |
|-------------|-------------------------------------|
| Backend     | Python 3 + Flask                    |
| Frontend    | HTML5, CSS3, Vanilla JavaScript     |
| Templating  | Jinja2 (Flask templates)            |
| Auth        | Flask sessions + werkzeug hashing   |
| Storage     | JSON files (no database required)   |

---

## 📂 Project Structure

```
crowdfunding/
├── app.py                    # Flask application (routes, config)
├── models.py                 # User & Project classes (with password hashing)
├── auth_manager.py           # Auth service (register, activate, login)
├── project_manager.py        # Project service (CRUD + search)
├── validators.py             # Validation functions (email, phone, date, etc.)
├── requirements.txt          # Python dependencies (Flask, Werkzeug)
├── data/
│   ├── users.json            # User data store
│   └── projects.json         # Project data store
├── templates/
│   ├── base.html             # Base template (navbar, flash messages, footer)
│   ├── register.html         # Registration form
│   ├── activate.html         # Account activation form
│   ├── login.html            # Login form
│   ├── dashboard.html        # Dashboard with navigation cards
│   ├── projects_list.html    # All projects listing
│   ├── project_create.html   # Create new project form
│   ├── project_edit.html     # Edit project form
│   ├── project_delete.html   # Delete confirmation page
│   ├── project_search.html   # Search by date form + results
│   ├── 404.html              # Custom 404 error page
│   └── 403.html              # Custom 403 permission denied page
├── static/
│   ├── css/
│   │   └── style.css         # Complete CSS design system
│   └── js/
│       └── script.js         # Client-side validation & UI interactions
├── .gitignore
└── README.md
```

---

## 🚀 Setup & Installation

### Prerequisites
- **Python 3.7+** installed on your system

### Steps

1. **Clone or navigate to the project directory:**
   ```bash
   cd crowdfunding
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application:**
   ```bash
   python app.py
   ```

4. **Open your browser and visit:**
   ```
   http://127.0.0.1:5000
   ```

---

## 🎯 Usage Flow

```
1. Register  →  2. See Activation Code  →  3. Activate Account  →  4. Login
                                                                        ↓
                                                              ┌─────────────────┐
                                                              │  Dashboard      │
                                                              │  Create Project │
                                                              │  View Projects  │
                                                              │  Edit Project   │
                                                              │  Delete Project │
                                                              │  Search by Date │
                                                              │  Logout         │
                                                              └─────────────────┘
```

---

## 📋 Architecture

- **Clean OOP design** with separation of concerns:
  - `models.py` — Data models only (User, Project)
  - `validators.py` — Pure validation functions
  - `auth_manager.py` — Authentication business logic
  - `project_manager.py` — Project CRUD business logic
  - `app.py` — Thin Flask routes that delegate to manager classes
- **Dual validation** — Client-side (JavaScript) + Server-side (Python)
- **Password security** — bcrypt-based hashing via werkzeug
- **Session-based auth** — Flask sessions with login_required decorator
- **Error handling** — Graceful handling of all invalid input, custom error pages

---

## 👨‍💻 Author

Built as a learning project to demonstrate Python Flask web development, OOP, authentication, CRUD operations, and responsive web design.
