from extensions import db


class User(db.Model):

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    name = db.Column(
        db.String(100),
        nullable=False
    )

    username = db.Column(
        db.String(100),
        unique=True,
        nullable=False
    )

    email = db.Column(
        db.String(100),
        unique=True,
        nullable=False
    )

    password = db.Column(
        db.String(255),
        nullable=False
    )

    phone = db.Column(
        db.String(20),
        nullable=True
    )

    role = db.Column(
        db.String(50),
        nullable=False,
        default="vendor"
    )

    def __repr__(self):
        return f"<User {self.username}>"


class Admin(db.Model):

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    username = db.Column(
        db.String(100),
        unique=True,
        nullable=False
    )

    email = db.Column(
        db.String(100),
        unique=True,
        nullable=False
    )

    password = db.Column(
        db.String(200),
        nullable=False
    )


class Quotation(db.Model):

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    rfq_id = db.Column(
        db.Integer,
        nullable=False
    )

    vendor_id = db.Column(
        db.Integer,
        nullable=False
    )

    price = db.Column(
        db.Float,
        nullable=False
    )

    delivery_days = db.Column(
        db.Integer,
        nullable=False
    )

    comments = db.Column(
        db.Text,
        nullable=True
    )

    status = db.Column(
        db.String(20),
        default="pending"
    )

    def __repr__(self):
        return f"<Quotation {self.id}>"