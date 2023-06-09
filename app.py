from flask import Flask, render_template, redirect, request, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import exc
from flask_migrate import Migrate

db = SQLAlchemy()
app = Flask(__name__)
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///cards.db"
migrate = Migrate(app, db)
db.init_app(app)

class Card(db.Model):
    __tablename__ = 'card'
    id = db.Column(db.Integer, primary_key=True)
    question = db.Column(db.String, unique=True, nullable=False)
    answer = db.Column(db.String, nullable=False)
    tag = db.Column(db.String)


with app.app_context():
    db.create_all()


@app.route("/")
def home():
    number = db.paginate(db.Select(Card)).total
    num_of_tags = db.paginate(db.select(Card.tag).distinct()).total
    return render_template("home.html", number=number, num_of_tags=num_of_tags)


@app.get("/info")
def get_info():
    return render_template("info.html")


@app.get("/create")
def new_kard():
    return render_template("create.html")


@app.route("/train", methods=["GET", "POST"])
def train():
    if request.method == "POST":
        filter = request.form.get("filter")
        if filter == "all":
            cards = db.session.execute(db.select(Card)).scalars()
        else:
            cards = db.session.execute(db.select(Card).where(Card.tag == filter)).scalars()
    else:
        cards = db.session.execute(db.select(Card)).scalars()
    tags = db.session.execute(db.select(Card.tag).distinct().order_by(Card.tag)).scalars()

    return render_template("base.html", cards=cards, tags=tags)


@app.post("/add")
def add_card():
    q = request.form.get("question")
    a = request.form.get("answer")
    t = request.form.get("tag").title()
    if not t:
        t = "Untagged"

    new_card = Card(question = q, answer = a, tag = t)

    try:
        db.session.add(new_card)
        db.session.commit()
    except exc.IntegrityError:
        flash("Card Already Exists!", 'error')
        return redirect("/")
    
    flash("Card Successfully added!", 'info')
    return redirect("/")


@app.route("/delete/<int:card_id>", methods=['GET', 'POST'])
def delete_card(card_id: int):
    if request.method == "POST":
        card = db.session.execute(db.select(Card).filter_by(id=card_id)).scalar_one()
        db.session.delete(card)
        db.session.commit()
        flash("Card Successfully deleted!", 'info')
        return redirect("/")
    else:
        return render_template("delete_card.html", card_id=card_id)
    

@app.route("/edit/<int:card_id>", methods=["GET", "POST"])
def edit_card(card_id: int):
    card = db.session.execute(db.select(Card).filter_by(id=card_id)).scalar_one()
    if request.method == "POST":
        try:
            card.question = request.form.get("question")
            card.answer = request.form.get("answer")
            db.session.commit()
        except exc.IntegrityError:
            flash("There's a card with this question alrady!", 'error')
            return redirect("/")
        
        flash("Card Successfully edited!", 'info')
        return redirect("/")
    else:
        return render_template("edit.html", card=card)


if __name__ == "__main__":
    app.run()