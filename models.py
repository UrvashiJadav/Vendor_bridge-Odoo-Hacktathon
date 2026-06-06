from extensions import db

class User(db.Model):

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    name = db.Column(
        db.String(100)
    )

    username = db.Column(
        db.String(100),
        unique=True
    )

    email = db.Column(
        db.String(100),
        unique=True
    )

    password = db.Column(
        db.String(255)
    )

    phone = db.Column(
        db.String(20)
    )

    role = db.Column(
        db.String(50),
        default="vendor"
    )

    def __repr__(self):
        return f"<User {self.username}>"

class Admin(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    username = db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)