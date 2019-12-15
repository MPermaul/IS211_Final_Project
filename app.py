from flask import flash, Flask, redirect, render_template, request, url_for
from flask_login import current_user, login_required, login_user, logout_user
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, UserMixin
from flask_wtf import FlaskForm
from urllib.request import urlopen
from wtforms import BooleanField, PasswordField, StringField, SubmitField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
import json
import os


# create Flask app object
app = Flask(__name__)

# appliction config section
app.config['DEBUG'] = False
app.config['SECRET_KEY'] = os.urandom(24)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///flask_book.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# create SQLAlchemy database object
db = SQLAlchemy(app)

# create flask bcrpyt object for password hashing and checks
bcrypt = Bcrypt(app)

# create flask login manager objects
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'

# glboal book variable initialzed as None
book = None

# classes used by Flask Application
class User(db.Model, UserMixin):
    """A class object representing a user table in a database."""
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(24), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=True)
    password = db.Column(db.String(24), nullable=False)
    books = db.relationship('Book', backref='user_books', lazy=True)


class Book(db.Model):
    """A class object representing a book table in a database."""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    title = db.Column(db.String(100), nullable=False)
    authors = db.Column(db.String(100), nullable=False )
    pages = db.Column(db.Integer, nullable=False)
    rating = db.Column(db.String(50), nullable=False)


class Book_Api():
    """A class object representing a book using data from a search."""

    def __init__ (self, title, authors, pages, rating):
        self.title = title
        self.authors = authors
        self.pages = pages
        self.rating = rating


class LoginForm(FlaskForm):
    """A class object representing a login form."""
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')


class IsbnForm(FlaskForm):
    """A class object representing a search form."""

    isbn = StringField('ISBN Number:', validators=[DataRequired()])
    submit = SubmitField('Search')


class AddForm(FlaskForm):
    """A class object representing a form used to add a book to a list."""

    submit = SubmitField('Add Book')

# book example for home page
books = [
    {
        'title': 'Flask Web Development',
        'author': 'Miguel Grinberg',
        'pages': 237,
        'rating': 'No Rating Available'
    }
]

# functions used by Flask Application
def Google_Search(isbn):
    """A function that takes in a book's isbn number and returns the json data if it exists.
    param: isbn: A string value representing a book's isbn number.
    return: jsonData: A json object with details of an isbn
    """

    # main google books api url
    api = "https://www.googleapis.com/books/v1/volumes?q=isbn:"

    # full url with passed in ISBN number
    url = api + isbn

    # connect to url and retrieve JSon data if response is ok
    try:
        with urlopen(url) as html:
            data = html.read()
    except:
        flash('Unable to Perform Search', 'danger')
        return redirect(url_for('search'))
    
    # load json data to variable
    jsonData = json.loads(data)
    
    return jsonData


def Process_Json(data):
    """A function that takes in a json object and processes it
    param: data: A json object containing data from a google api book search.
    return: book: A class Book object with details of book.
    """

    # set variables based on JSon data
    title = data["items"][0]["volumeInfo"]["title"]
    authors = data["items"][0]["volumeInfo"]["authors"]
    pages = data["items"][0]["volumeInfo"]["pageCount"]

    # check to see if there is a rating
    try:
        rating = data["items"][0]["volumeInfo"]["averageRating"]
    except:
        # set rating value if none found
        rating = 'No Rating Available'

    # set variable that will store string of authors
    authors_list = ''

    # check to see if there is more than one author
    if len(authors) > 1:

        # loop through list of authors
        for author in authors:

            # update authors_list to include string of author and a blank space
            authors_list += author
            authors_list += ' '
    else:
        # set authors_list to single author
        authors_list = authors[0]

    # create book object with json data
    book = Book_Api(title=title, authors=authors_list, pages=pages, rating=rating)
    
    # return the book object
    return book


# routes used by Flask Application
@app.route("/")
@app.route("/home")
def home():
    return render_template('home.html', books=books)


@app.route("/login", methods=['GET', 'POST'])
def login():
    
    # if user is already logged in, redirect to home page
    if current_user.is_authenticated:
        return redirect(url_for('account'))
    
    # set form to login form
    form = LoginForm()

    # check when login button is pressed
    if form.validate_on_submit():

        # set user to username from login form
        user = User.query.filter_by(username=form.username.data).first()
        
        # if username and hassed password match account in database
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            
            # call login user function, pass in user, and flash message 
            login_user(user)
            next_page = request.args.get('next')
            flash('Login Successful', 'success')
            return redirect(next_page) if next_page else redirect(url_for('account'))
        else:
            # flash error message
            flash('Login Unsuccessful. Check Username and Password', 'danger')
    
    return render_template('login.html', form=form)


@app.route("/logout")
def logout():

    # call logout user function from Flask
    logout_user()
    
    # flash message and redirect to home page
    flash('Logout Successful', 'success')
    return redirect(url_for('home'))


@app.route("/account")
@login_required
def account():

    # query database to get all books
    catalogue = Book.query.all()

    return render_template('account.html', catalogue=catalogue)


@app.route("/search", methods=['GET', 'POST'])
@login_required
def search():

    global book

    # set form to ISBN form
    form = IsbnForm()

    # check if search button is pressed
    if form.validate_on_submit():
        # call search function and pass in isbn number
        json_response = Google_Search(form.isbn.data)
        
        # if json respons has 0 total items
        if json_response["totalItems"] == 0:
            flash('No Book Found!', 'danger')
            return redirect(url_for('search'))
        else:
            # call process function and pass in json data
            book = Process_Json(json_response)
            # redirect to add book page
            return redirect(url_for('add_book'))

    return render_template('search.html', form=form)


@app.route("/add_book", methods=['GET', 'POST'])
@login_required
def add_book():

    # use global book variable
    global book

    # set form to add form
    form = AddForm()
    
    # check if search button is pressed
    if form.validate_on_submit():
       
        # set new book object that will be inserted into database
        new_book = Book(user_id=current_user.get_id() , title=book.title, authors=book.authors, pages=book.pages, rating=book.rating)

        # do a check to see if new book's title already exists in database
        book_check = Book.query.filter_by(title=new_book.title).first()

        # if book title exists
        if book_check:
            # flash message and redirect to account page
            flash('Book Already Exists', 'danger')
            return redirect(url_for('account'))
        
        try:
            # try to add new book to database
            db.session.add(new_book)
            db.session.commit()
            flash('Book Added to Catalogue List', 'success')
            return redirect(url_for('account'))
        except:
            # flash message and redirect to account page
            flash('Database Error - Unable to Add Book to List', 'danger')
            return redirect(url_for('account'))

    return render_template('add_book.html', book=book, form=form)


@app.route("/<int:book_id>/delete", methods=['GET', 'POST'])
@login_required
def delete_book(book_id):
    
    try:
        # set book equal to book to delete
        book = Book.query.get_or_404(book_id)
        # run query to delete book and set flash message
        db.session.delete(book)
        db.session.commit()
        flash('Book Deleted', 'success')
    except:
        # flash database error message 
        flash('Database Error - Unable to Delete Book', 'danger')
    finally:
        # redirect to account page
        return redirect(url_for('account'))


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


if __name__ == '__main__':

    app.run()