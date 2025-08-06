from flask import Flask, render_template, request, redirect, url_for
from wtforms import Form, StringField, FloatField
from wtforms.validators import DataRequired, NumberRange
from flask_wtf import FlaskForm
from sqlalchemy import Integer, String, Float
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from flask_sqlalchemy import SQLAlchemy


class AddForm(FlaskForm):
    title = StringField("Title", validators=[DataRequired()])
    author = StringField("Author", validators=[DataRequired()])
    rating = FloatField("Rating", validators=[DataRequired(), NumberRange(0.0, 10.0)])


class RatingForm(FlaskForm):
    rating = FloatField("New Rating", validators=[DataRequired(), NumberRange(0.0, 10.0)])


class Base(DeclarativeBase):
    pass


db = SQLAlchemy(model_class=Base)
app = Flask(__name__)
app.config["SECRET_KEY"] = "supersecret"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///new-books-collection.db"
db.init_app(app)


class Book(db.Model):
    __tablename__ = "books"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(250), nullable=False, unique=True)
    author: Mapped[str] = mapped_column(String(250), nullable=False)
    rating: Mapped[float] = mapped_column(Float, nullable=False)


with app.app_context():
    db.create_all()


@app.route("/")
def home():
    return render_template("index.html", books=db.session.query(Book).all())


@app.route("/add", methods=["GET", "POST"])
def add():
    form = AddForm()
    if form.validate_on_submit():
        with app.app_context():
            book = Book(title=form.title.data, author=form.author.data, rating=form.rating.data)
            db.session.add(book)
            db.session.commit()
    return render_template("add.html", form = form)


@app.route("/edit", methods=["GET", "POST"])
def edit():
    form = RatingForm()
    if form.validate_on_submit():
        with app.app_context():
            db.session.query(Book).where(Book.id == request.args["id"]).update({"rating": form.rating.data})
            db.session.commit()
        return redirect("/")

    book = db.session.query(Book).where(Book.id == request.args["id"]).first()
    return render_template("edit.html", form=form, book=book)


@app.route("/delete")
def delete():
    with app.app_context():
        db.session.query(Book).where(Book.id == request.args["id"]).delete()
        db.session.commit()
    return redirect("/")


if __name__ == "__main__":
    app.run(debug=True)