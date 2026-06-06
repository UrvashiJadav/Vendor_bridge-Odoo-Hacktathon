import smtplib
from email.mime.text import MIMEText
import random

from flask import Flask, request, jsonify, render_template, session, redirect
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash

from extensions import db
from models import User, Quotation

app = Flask(__name__)
CORS(app)

# ==========================
# SESSION
# ==========================
app.secret_key = "vendor_bridge_secret_key"

# ==========================
# DB CONFIG
# ==========================
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

with app.app_context():
    db.create_all()

# ==========================
# ADMIN
# ==========================
HARDCODED_ADMIN = {
    "username": "admin",
    "email": "admin@gmail.com",
    "password": "admin123"
}

# ==========================
# OTP STORAGE
# ==========================
otp_storage = {}

def send_email_otp(receiver_email, otp):
    sender_email = "demohackathon2026@gmail.com"
    app_password = "udrz wxzt argm zkfm"

    msg = MIMEText(f"Your OTP is: {otp}")
    msg["Subject"] = "Password Reset OTP"
    msg["From"] = sender_email
    msg["To"] = receiver_email

    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.starttls()
    server.login(sender_email, app_password)
    server.send_message(msg)
    server.quit()

# ==========================
# PAGES
# ==========================
@app.route('/')
def register_page():
    return render_template('register.html')

@app.route('/login')
def login_page():
    return render_template('login.html')

@app.route('/home')
def home_page():
    return render_template('home.html')

@app.route('/admin')
def admin_page():
    return render_template('admin_dashboard.html')

@app.route('/manager')
def manager_page():
    return render_template('manager_dashboard.html')

@app.route('/vendor-dashboard')
def vendor_dashboard():
    if session.get("role") != "vendor":
        return redirect("/login")
    return render_template('vendor_dashboard.html')

@app.route('/vendor-rfqs')
def vendor_rfqs():
    return render_template('vendor_rfqs.html')

@app.route('/submit-quotation-page')
def submit_quotation_page():
    return render_template('submit_quotation.html')

@app.route('/my-quotations')
def my_quotations():
    return render_template('my_quotations.html')

# ==========================
# REGISTER
# ==========================
@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()

    if User.query.filter_by(username=data.get("username")).first():
        return jsonify({"status": "error", "message": "Username exists"})

    if User.query.filter_by(email=data.get("email")).first():
        return jsonify({"status": "error", "message": "Email exists"})

    user = User(
        name=data.get("name"),
        username=data.get("username"),
        email=data.get("email"),
        password=generate_password_hash(data.get("password")),
        phone=data.get("phone"),
        role="vendor"
    )

    db.session.add(user)
    db.session.commit()

    return jsonify({"status": "success", "message": "Registered"})

# ==========================
# LOGIN (SESSION FIXED)
# ==========================
@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()

    username = data.get("username", "").strip().lower()
    email = data.get("email", "").strip().lower()
    password = data.get("password")

    # ADMIN
    if username == HARDCODED_ADMIN["username"] and email == HARDCODED_ADMIN["email"]:
        if password == HARDCODED_ADMIN["password"]:
            session.clear()
            session["role"] = "admin"
            session["username"] = "admin"

            return jsonify({
                "status": "success",
                "role": "admin"
            })

    # USER
    user = User.query.filter(
        (User.username == username) |
        (User.email == email)
    ).first()

    if not user:
        return jsonify({"status": "error", "message": "User not found"})

    if not check_password_hash(user.password, password):
        return jsonify({"status": "error", "message": "Wrong password"})

    session.clear()
    session["role"] = user.role
    session["user_id"] = user.id
    session["username"] = user.username

    return jsonify({
        "status": "success",
        "role": user.role,
        "user_id": user.id
    })

# ==========================
# POST LOGIN REDIRECT FIX
# ==========================
@app.route('/post-login')
def post_login():
    role = session.get("role")

    if role == "admin":
        return redirect("/admin")

    elif role == "manager":
        return redirect("/manager")

    elif role == "vendor":
        return redirect("/vendor-dashboard")

    return redirect("/login")

# ==========================
# CREATE EMPLOYEE (FIXED 404 ISSUE)
# ==========================
@app.route('/create-employee', methods=['POST'])
def create_employee():

    data = request.get_json()

    if User.query.filter_by(username=data.get("username")).first():
        return jsonify({"status": "error", "message": "Username exists"})

    if User.query.filter_by(email=data.get("email")).first():
        return jsonify({"status": "error", "message": "Email exists"})

    user = User(
        name=data.get("name"),
        username=data.get("username"),
        email=data.get("email"),
        password=generate_password_hash(data.get("password")),
        role=data.get("role")
    )

    db.session.add(user)
    db.session.commit()

    return jsonify({
        "status": "success",
        "message": "Employee Created Successfully"
    })

# ==========================
# OTP SYSTEM
# ==========================
@app.route('/send-otp', methods=['POST'])
def send_otp():
    data = request.get_json()
    email = data.get("email")

    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify({"status": "error", "message": "Email not registered"})

    otp = str(random.randint(100000, 999999))
    otp_storage[email] = otp

    send_email_otp(email, otp)

    return jsonify({"status": "success", "message": "OTP Sent"})

@app.route('/verify-otp', methods=['POST'])
def verify_otp():
    data = request.get_json()

    email = data.get("email")
    otp = data.get("otp")

    if otp_storage.get(email) != otp:
        return jsonify({"status": "error", "message": "Invalid OTP"})

    return jsonify({"status": "success", "message": "Verified"})

@app.route('/reset-password', methods=['POST'])
def reset_password():
    data = request.get_json()

    user = User.query.filter_by(email=data.get("email")).first()
    if not user:
        return jsonify({"status": "error", "message": "User not found"})

    user.password = generate_password_hash(data.get("password"))
    db.session.commit()

    otp_storage.pop(data.get("email"), None)

    return jsonify({"status": "success", "message": "Password updated"})

# ==========================
# QUOTATIONS
# ==========================
@app.route('/submit-quotation', methods=['POST'])
def submit_quotation():
    data = request.get_json()

    quotation = Quotation(
        rfq_id=data.get("rfq_id"),
        vendor_id=data.get("vendor_id"),
        price=data.get("price"),
        delivery_days=data.get("delivery_days"),
        comments=data.get("comments"),
        status="pending"
    )

    db.session.add(quotation)
    db.session.commit()

    return jsonify({"status": "success", "message": "Quotation submitted"})

@app.route('/get-quotations')
def get_quotations():
    quotations = Quotation.query.all()

    return jsonify([
        {
            "id": q.id,
            "rfq_id": q.rfq_id,
            "price": q.price,
            "delivery_days": q.delivery_days,
            "comments": q.comments,
            "status": q.status
        }
        for q in quotations
    ])

# ==========================
# RUN
# ==========================
if __name__ == "__main__":
    app.run(debug=True)