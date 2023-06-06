from flask import Flask, render_template, redirect, request, url_for
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///cards.db"
db.init_app(app)

class Card(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    question = db.Column(db.String, unique=True, nullable=False)
    answer = db.Column(db.String, nullable=False)

class Collection(db.Model):
    __tablename__ = 'collections'
    id = db.Column(db.Integer, primary_key=True)
    card_id = db.Column(db.Integer, db.ForeignKey('card.id'))

with app.app_context():
    db.create_all()

@app.route("/")
def home():
    return render_template("home.html")

@app.route("/train")
def train():
    cards = db.session.execute(db.select(Card)).scalars()
    return render_template("base.html", cards=cards)

@app.post("/add")
def add_card():
    q = request.form.get("question")
    a = request.form.get("answer")

    new_card = Card(question = q, answer = a)
    db.session.add(new_card)
    db.session.commit()

    return redirect("/")

@app.get("/delete/<int:card_id>")
def delete_card(card_id: int):
    card = db.session.execute(db.select(Card).filter_by(id=card_id)).scalar_one()
    db.session.delete(card)
    db.session.commit()
    return redirect("/")

@app.route("/edit/<int:card_id>", methods=["GET", "POST"])
def edit_card(card_id: int):
    card = db.session.execute(db.select(Card).filter_by(id=card_id)).scalar_one()
    if request.method == "POST":
        card.question = request.form.get("question")
        card.answer = request.form.get("answer")
        db.session.commit()
        return redirect("/")
    else:
        return render_template("edit.html", card=card)


if __name__ == "__main__":
    app.run()