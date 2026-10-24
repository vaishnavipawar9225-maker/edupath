# 🎓 EduPath - Full Stack EdTech Platform

![Django](https://img.shields.io/badge/Django-092E20?style=for-the-badge&logo=django&logoColor=white)
![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-316192?style=for-the-badge&logo=postgresql&logoColor=white)
![Bootstrap](https://img.shields.io/badge/Bootstrap-563D7C?style=for-the-badge&logo=bootstrap&logoColor=white)

EduPath is a modern, full-stack Learning Management System (LMS) designed specifically for students in Classes 5 to 10 in India. It provides a seamless experience for Students, Teachers, Parents, and Administrators, featuring course management, auto-generated quizzes, live classes, and a comprehensive parent portal.

## 🌐 Live Demo
**URL:** [https://edupath-g18h.onrender.com](https://edupath-g18h.onrender.com)
*(Note: Hosted on Render's free tier, it might take 30-50 seconds to wake up if inactive).*

### 🔑 Demo Credentials
| Role | Username | Password |
| :--- | :--- | :--- |
| **Admin** | `admin` | `admin12345` |
| **Teacher** | `verma` | `pass12345` |
| **Student** | `riya` | `pass12345` |
| **Parent** | `parent1` | `pass12345` |

---

## ✨ Key Features

### 👨‍🎓 Student Portal
*   **Course Discovery:** Browse courses by Class (5–10) with a beautiful UI.
*   **Mock Payments:** Enroll in paid courses using a simulated UPI/Card/Netbanking checkout. Apply coupons (e.g., `SAVE20`).
*   **PDF Receipts:** Download automated PDF receipts for successful payments.
*   **Interactive Quizzes:** Take timed quizzes with a live countdown, progress bar, and auto-scoring.
*   **Live Classes:** Join scheduled video classes directly via Jitsi Meet integration.
*   **Progress Tracking:** View personal quiz history and attendance percentage.

### 👨‍🏫 Teacher Portal
*   **Quiz Management:** Create quizzes instantly. The system auto-generates topic-specific questions based on the course subject (Math, Physics, Grammar).
*   **Attendance Marking:** Mark daily attendance for enrolled students.
*   **Live Class Scheduling:** Schedule video sessions for courses.
*   **Parent Meetings:** Accept or reject Parent-Teacher Meeting (PTM) requests.

### 👨‍👩‍👧 Parent Portal
*   **Link Child:** Securely link a student's account using their email address.
*   **Analytics Dashboard:** Track child's performance via interactive **Chart.js** graphs (Quiz scores bar chart & Attendance doughnut chart).
*   **PTM Requests:** Request and join video meetings with teachers.

### 🛡️ Admin Portal
*   **Custom Dashboard:** High-level overview of Total Users, Courses, Enrollments, and Revenue.
*   **Django Admin Integration:** Full CRUD access to all 18+ database tables.
*   **Payment Management:** View all transactions, issue refunds, and manage discount coupons.

---

## 💻 Tech Stack

*   **Backend:** Python 3, Django 5/6
*   **Frontend:** HTML5, CSS3 (Custom Design System), JavaScript (ES6)
*   **Database:** SQLite (Development), PostgreSQL (Production)
*   **Third-Party APIs:**
    *   **Jitsi Meet:** Embedded video calls for live classes and PTMs.
    *   **Razorpay:** Mock payment gateway integration (ready for production keys).
    *   **Chart.js:** Data visualization for parent dashboards.
    *   **SweetAlert2:** Beautiful modal alerts for quiz submissions and payments.
    *   **ReportLab:** Automated PDF generation for payment receipts.
*   **Deployment:** Gunicorn, WhiteNoise, Render.

---

## 🚀 Local Installation & Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/Shweta-281/edupath.git
   cd edupath

2. **Create and activate a virtual environment:**
   ```bash
   python -m venv venv
   # Windows
   venv\Scripts\activate
   # Mac/Linux
   source venv/bin/activate 

3. **Install dependencies:**
    ```bash
    pip install -r requirements.txt

4. **Set up Environment Variables:**
 Create a .env file in the root directory and add the following:
   ```bash
   SECRET_KEY=your_secret_key_here
   DEBUG=True
   DB_ENGINE=django.db.backends.sqlite3

5. **Run Migrations:**
    ```bash
    python manage.py makemigrations
    python manage.py migrate

6. **Seed Demo Data (Creates users, courses, and quizzes):**
   ```bash
   python manage.py seed_demo_data

7. **Start the development server:**
   ```bash
   python manage.py runserver
   
 Open http://127.0.0.1:8000 in your browser.