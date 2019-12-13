# IS211_Final_Project
Final Project for IS211

Author: Moses Permaul - moses.permaul13@spsmail.cuny.edu

Requirements:

This application Flask, Flask Bcrypt, Flask Login, Flask WTF Forms, and SQLAlchemy. If you need to install these, you can run the following command to have it installed:

    pip install flask
    pip install flask-bcrypt
    pip install falsk-login
    pip install flask-sqlalchemy
    pip install flask-wtf

Application Details:

1) This applicaiton is a Flask Web app of a Book Catalogue that allows a user to login to the website in order to search and store book they own.

2) The data for the user and books are stored in a sqlite3 database.

3) The main homepage loads when not logged in. It shows an example of what a book added to the book catalouge looks like.

4) When logged in, the user is taken to their book list. Each book has an option to delete it from the list.

5) On the right side of the webpage is a search link that allows a logged in user to access the ISBN search page.

6) When searching for a book, the results will be displayed with an option add the book to their list.


Demo Account Details:

    Username: DemoAccount
    Password: Password1