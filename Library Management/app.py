from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
import os
import datetime
app = Flask(__name__)
app.config['TEMPLATES_AUTO_RELOAD'] = True
app.secret_key = 'your_secret_key_here'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///library.db'
db = SQLAlchemy(app)
class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    author = db.Column(db.String(100), nullable=False)
class Member(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    def __repr__(self):
        return f"<Member {self.name}>"
class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    member_id = db.Column(db.Integer, db.ForeignKey('member.id'), nullable=False)
    book_id = db.Column(db.Integer, db.ForeignKey('book.id'), nullable=False)
    issue_date = db.Column(db.DateTime, default=datetime.datetime.now)
    return_date = db.Column(db.DateTime)
    member = db.relationship('Member', backref=db.backref('transactions', lazy=True))
    book = db.relationship('Book', backref=db.backref('transactions', lazy=True))
def authenticate_user(username, password):
    return username == 'vijay' and password == 'password'
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if authenticate_user(username, password):
            session['username'] = username
            flash('Login successful!', 'success')
            return redirect(url_for('home'))
        else:
            flash('Invalid credentials. Please try again.', 'danger')
    return render_template('login.html')
@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))
@app.route('/')
def home():
    if 'username' in session:
        return render_template('home.html', username=session['username'])
    else:
        return redirect(url_for('login'))
@app.route('/add_book', methods=['GET', 'POST'])
def add_book():
    if 'username' not in session:
        flash('Please login first.', 'danger')
        return redirect(url_for('login'))
    if request.method == 'POST':
        title = request.form['title']
        author = request.form['author']
        new_book = Book(title=title, author=author)
        db.session.add(new_book)
        db.session.commit()
        flash('Book added successfully!', 'success')
        return redirect(url_for('view_books'))
    return render_template('add_book.html')
@app.route('/add_member', methods=['GET', 'POST'])
def add_member():
    if 'username' not in session:
        flash('Please login first.', 'danger')
        return redirect(url_for('login'))
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        new_member = Member(name=name, email=email)
        db.session.add(new_member)
        db.session.commit()
        flash('Member added successfully!', 'success')
        return redirect(url_for('view_members'))
    return render_template('add_member.html')
@app.route('/view_books')
def view_books():
    if 'username' not in session:
        flash('Please login first.', 'danger')
        return redirect(url_for('login'))
    books = Book.query.all()
    return render_template('view_books.html', books=books)
@app.route('/view_members')
def view_members():
    if 'username' not in session:
        flash('Please login first.', 'danger')
        return redirect(url_for('login'))
    members = Member.query.all()
    return render_template('view_members.html', members=members)
@app.route('/issue_book', methods=['GET', 'POST'])
def issue_book():
    if 'username' not in session:
        flash('Please login first.', 'danger')
        return redirect(url_for('login'))
    if request.method == 'POST':
        member_id = request.form['member_id']
        book_id = request.form['book_id']
        member = Member.query.get(member_id)
        book = Book.query.get(book_id)
        if not member or not book:
            flash('Invalid member ID or book ID. Please try again.', 'danger')
        else:
            new_transaction = Transaction(member_id=member_id, book_id=book_id)
            db.session.add(new_transaction)
            db.session.commit()
            flash('Book issued successfully!', 'success')
        return redirect(url_for('issue_book'))
    members = Member.query.all()
    books = Book.query.all()
    return render_template('issue_book.html', members=members, books=books)
@app.route('/search')
def search():
    if 'username' not in session:
        flash('Please login first.', 'danger')
        return redirect(url_for('login'))
    books_count = Book.query.count()
    members_count = Member.query.count()
    active_transactions_count = Transaction.query.filter_by(return_date=None).count()
    return render_template('search.html', username=session['username'], books_count=books_count, members_count=members_count, active_transactions_count=active_transactions_count)
@app.route('/return_book', methods=['GET', 'POST'])
def return_book():
    if 'username' not in session:
        flash('Please login first.', 'danger')
        return redirect(url_for('login'))
    if request.method == 'POST':
        transaction_id = request.form['transaction_id']
        transaction = Transaction.query.get(transaction_id)
        if transaction:
            transaction.return_date = datetime.datetime.now()
            db.session.commit()
            flash('Book returned successfully!', 'success')
        else:
            flash('Invalid transaction ID. Please try again.', 'danger')

        return redirect(url_for('return_book'))
    active_transactions = Transaction.query.filter_by(return_date=None).all()
    return render_template('return_book.html', active_transactions=active_transactions)
@app.route('/view_transactions')
def view_transactions():
    if 'username' not in session:
        flash('Please login first.', 'danger')
        return redirect(url_for('login'))
    transactions = Transaction.query.all()
    return render_template('view_transactions.html', transactions=transactions)
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)