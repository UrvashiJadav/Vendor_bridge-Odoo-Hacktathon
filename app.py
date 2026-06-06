import smtplib
from email.mime.text import MIMEText
import random

from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash

from extensions import db
from models import User, Quotation   # ✅ IMPORTANT FIX: Quotation added

app = Flask(__name__)
CORS(app)

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

    subject = "Password Reset OTP"

    body = f"""
Your OTP is: {otp}

Do not share this OTP with anyone.
"""

    msg = MIMEText(body)
    msg["Subject"] = subject
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

@app.route('/forgot-password')
def forgot_password_page():
    return render_template('forgot_password.html')

@app.route('/vendor-dashboard')
def vendor_dashboard():
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

    reqdata = request.get_json()

    name = reqdata.get("name")
    username = reqdata.get("username")
    email = reqdata.get("email")
    password = reqdata.get("password")
    phone = reqdata.get("phone")

    if not name or not name.strip():
        return jsonify({"status": "error", "message": "Invalid Name"})

    if not username or not username.strip():
        return jsonify({"status": "error", "message": "Invalid Username"})

    if not email or not email.strip():
        return jsonify({"status": "error", "message": "Invalid Email"})

    if not password or not password.strip():
        return jsonify({"status": "error", "message": "Invalid Password"})

    if User.query.filter_by(username=username).first():
        return jsonify({"status": "error", "message": "Username already exists"})

    if User.query.filter_by(email=email).first():
        return jsonify({"status": "error", "message": "Email already exists"})

    new_user = User(
        name=name,
        username=username,
        email=email,
        password=generate_password_hash(password),
        phone=phone,
        role="vendor"
    )

    db.session.add(new_user)
    db.session.commit()

    return jsonify({"status": "success", "message": "Registration Successful"})

# ==========================
# LOGIN
# ==========================
@app.route('/login', methods=['POST'])
def login():

    reqdata = request.get_json()

    username = reqdata.get("username")
    email = reqdata.get("email")
    password = reqdata.get("password")

    username = username.strip().lower()
    email = email.strip().lower()

    # Admin login
    if (
        username == HARDCODED_ADMIN["username"]
        and email == HARDCODED_ADMIN["email"]
        and password == HARDCODED_ADMIN["password"]
    ):
        return jsonify({
            "status": "success",
            "message": "Admin Login Success",
            "role": "admin",
            "username": "admin"
        })

    user = User.query.filter(
        (User.username == username) |
        (User.email == email)
    ).first()

    if not user:
        return jsonify({"status": "error", "message": "User not found"})

    if not check_password_hash(user.password, password):
        return jsonify({"status": "error", "message": "Wrong Password"})

    return jsonify({
        "status": "success",
        "message": "Login Successful",
        "role": user.role,
        "username": user.username,
        "user_id": user.id
    })

# ==========================
# OTP
# ==========================
@app.route('/send-otp', methods=['POST'])
def send_otp():

    reqdata = request.get_json()
    email = reqdata.get("email")

    user = User.query.filter_by(email=email).first()

    if not user:
        return jsonify({"status": "error", "message": "Email not registered"})

    otp = str(random.randint(100000, 999999))
    otp_storage[email] = otp

    send_email_otp(email, otp)

    return jsonify({"status": "success", "message": "OTP Sent Successfully"})

@app.route('/verify-otp', methods=['POST'])
def verify_otp():

    reqdata = request.get_json()

    email = reqdata.get("email")
    otp = reqdata.get("otp")

    if otp_storage.get(email) != otp:
        return jsonify({"status": "error", "message": "Invalid OTP"})

    return jsonify({"status": "success", "message": "OTP Verified Successfully"})

@app.route('/reset-password', methods=['POST'])
def reset_password():

    reqdata = request.get_json()

    email = reqdata.get("email")
    password = reqdata.get("password")

    user = User.query.filter_by(email=email).first()

    if not user:
        return jsonify({"status": "error", "message": "User not found"})

    user.password = generate_password_hash(password)
    db.session.commit()

    otp_storage.pop(email, None)

    return jsonify({"status": "success", "message": "Password Updated Successfully"})

# ==========================
# EMPLOYEE
# ==========================
@app.route('/create-employee', methods=['POST'])
def create_employee():

    reqdata = request.get_json()

    user = User(
        name=reqdata.get("name"),
        username=reqdata.get("username"),
        email=reqdata.get("email"),
        password=generate_password_hash(reqdata.get("password")),
        role=reqdata.get("role")
    )

    db.session.add(user)
    db.session.commit()

    return jsonify({"status": "success", "message": "Employee Created Successfully"})

# ==========================
# 🔥 FIXED PART (THIS WAS MISSING)
# ==========================
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
            "status": q.status if hasattr(q, "status") else "pending"
        }
        for q in quotations
    ])

# ==========================
# RUN
# ==========================
if __name__ == "__main__":
    app.run(debug=True)