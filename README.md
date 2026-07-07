# 🚀 Crowdfunding Platform — Console Application

A **console-based (CLI) crowdfunding application** built with Python, inspired by platforms like Kickstarter and GoFundMe. Users can register, activate their accounts, log in, and manage fundraising campaigns (projects).

---

## ✨ Features

### Authentication System
- **Registration** with full validation (name, email, phone, password)
- **Account Activation** via a generated activation code (printed to console)
- **Login** with email/password — inactive accounts are blocked

### Project Management (CRUD)
- **Create** new crowdfunding projects linked to your account
- **View** all projects from all users
- **Edit** your own projects (owner-only, with permission checks)
- **Delete** your own projects (owner-only, with confirmation prompt)
- **Search** projects by a specific date or date range (bonus feature)

### Validation
- Email format validation (regex)
- Egyptian mobile phone validation (010/011/012/015 + 8 digits)
- Date format validation (YYYY-MM-DD) with calendar correctness
- End-date-after-start-date enforcement
- Positive number validation for target amounts
- Non-empty field checks for all required inputs
- Password confirmation matching

### Data Persistence
- All data is saved to **JSON files** (`users.json`, `projects.json`)
- Data persists between program runs

---

## 📂 Project Structure

```
crowdfunding/
├── main.py              # Entry point — menu-driven CLI interface
├── models.py            # User and Project data classes
├── validators.py        # Reusable validation functions
├── auth_manager.py      # Registration, activation, login logic
├── project_manager.py   # Project CRUD + date search
├── users.json           # Auto-generated user data store
├── projects.json        # Auto-generated project data store
├── .gitignore           # Git ignore rules
└── README.md            # This file
```

---

## 🛠️ How to Run

### Prerequisites
- **Python 3.7+** installed on your system

### Steps

1. **Clone or navigate to the project directory:**
   ```bash
   cd crowdfunding
   ```

2. **Run the application:**
   ```bash
   python main.py
   ```

3. **Follow the on-screen menus:**
   - Register a new account
   - Activate it using the code shown during registration
   - Log in and start creating projects!

---

## 🎯 Usage Flow

```
1. Register  →  2. Activate Account  →  3. Login
                                             ↓
                                    ┌─────────────────┐
                                    │  Create Project  │
                                    │  View Projects   │
                                    │  Edit Project    │
                                    │  Delete Project  │
                                    │  Search by Date  │
                                    │  Logout          │
                                    └─────────────────┘
```

---

## 📋 Technical Details

- **Language:** Python 3
- **Architecture:** Clean OOP with separation of concerns
  - `models.py` — Data models only
  - `validators.py` — Pure validation functions
  - `auth_manager.py` — Authentication business logic
  - `project_manager.py` — Project business logic
  - `main.py` — UI/menu layer
- **Persistence:** JSON file-based storage
- **Error Handling:** try/except throughout to prevent crashes

---

## 👨‍💻 Author

Built as a learning project to demonstrate Python OOP, file I/O, regex validation, and clean code architecture.
