import smtplib
from email.mime.text import MIMEText
import random

from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash

from extensions import db
from models import User

app = Flask(__name__)
CORS(app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

with app.app_context():
    db.create_all()

HARDCODED_ADMIN = {
    "username": "admin",
    "email": "admin@gmail.com",
    "password": "admin123"
}

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

    existing_username = User.query.filter_by(username=username).first()
    if existing_username:
        return jsonify({"status": "error", "message": "Username already exists"})

    existing_email = User.query.filter_by(email=email).first()
    if existing_email:
        return jsonify({"status": "error", "message": "Email already exists"})

    hashed_password = generate_password_hash(password)

    new_user = User(
        name=name,
        username=username,
        email=email,
        password=hashed_password,
        phone=phone,
        role="vendor"
    )

    db.session.add(new_user)
    db.session.commit()

    return jsonify({
        "status": "success",
        "message": "Registration Successful"
    })

@app.route('/login', methods=['POST'])
def login():

    reqdata = request.get_json()

    username = reqdata.get("username")
    email = reqdata.get("email")
    password = reqdata.get("password")

    if not username or not username.strip():
        return jsonify({
            "status": "error",
            "message": "Invalid Username"
        })

    if not email or not email.strip():
        return jsonify({
            "status": "error",
            "message": "Invalid Email"
        })

    if not password or not password.strip():
        return jsonify({
            "status": "error",
            "message": "Invalid Password"
        })

    username = username.strip().lower()
    email = email.strip().lower()

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
        return jsonify({
            "status": "error",
            "message": "User not found"
        })

    if not check_password_hash(user.password, password):
        return jsonify({
            "status": "error",
            "message": "Wrong Password"
        })

    return jsonify({
        "status": "success",
        "message": "Login Successful",
        "role": user.role,
        "username": user.username
    })

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

    stored_otp = otp_storage.get(email)

    if not stored_otp:
        return jsonify({"status": "error", "message": "OTP not generated"})

    if otp != stored_otp:
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

    if email in otp_storage:
        del otp_storage[email]

    return jsonify({"status": "success", "message": "Password Updated Successfully"})

@app.route('/create-employee', methods=['POST'])
def create_employee():

    reqdata = request.get_json()

    name = reqdata.get("name")
    username = reqdata.get("username")
    email = reqdata.get("email")
    password = reqdata.get("password")
    role = reqdata.get("role")

    existing = User.query.filter(
        (User.username == username) |
        (User.email == email)
    ).first()

    if existing:
        return jsonify({
            "status":"error",
            "message":"User already exists"
        })

    user = User(
        name=name,
        username=username,
        email=email,
        password=generate_password_hash(password),
        role=role
    )

    db.session.add(user)
    db.session.commit()

    return jsonify({
        "status":"success",
        "message":"Employee Created Successfully"
    })

if __name__ == "__main__":
    app.run(debug=True)

