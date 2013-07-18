from flask import Flask, request, session, g, redirect, url_for, abort, render_template, flash, _app_ctx_stack
import sqlite3

DATABASE = '/tmp/lib.db'
DEBUG = True
SECRET_KEY = 'verysecretkey'
USERNAME = 'username'
PASSWORD = 'password'

app = Flask(__name__)
app.config.from_object(__name__)
app.config.from_envvar('LIB_SETTINGS', silent=True)

def init_db():
    with app.app_context():
        db = get_db()
        with app.open_resource('schema.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()

def get_db():
    top = _app_ctx_stack.top
    if not hasattr(top, 'sqlite_db'):
        sqlite_db = sqlite3.connect(app.config['DATABASE'])
        sqlite_db.row_factory = sqlite3.Row
        top.sqlite_db = sqlite_db
    return top.sqlite_db

@app.teardown_appcontext
def close_db_connection(exception):
    top = _app_ctx_stack.top
    if hasattr(top, 'sqlite_db'):
        top.sqlite_db.close()

@app.route('/')
def show_entries():
    db = get_db()
    cur = db.execute('select author, book from entries')
    entries = cur.fetchall()
    return render_template('show_entries.html', entries=entries)

@app.route('/add_entry', methods=['POST'])
def add_entry():
    if not session.get('logged_in'):
        abort(401)
    db = get_db()
    db.execute('insert into authors (author) values (?)',[request.form['author']])
    db.execute('insert into books (book) values (?)',[request.form['book']])
    db.execute('insert into authorsbooks(idauthor) select id from authors')
    db.execute('insert into authorsbooks(idbook) select id from books')
    db.commit()
    flash('New entry was successfully added')
    return redirect(url_for('show_entries'))

@app.route('/search_author',methods=['POST'])
def search_author():
    db = get_db()
    db.execute('insert into entries (book) select books.book from books inner join authorsbooks on\
                books.id=authorsbooks.idbook inner join authors on \
                authorsbooks.idauthor=authors.id where authors.author=values(?)' , [request.form['searchauthor']])
    db.execute('insert into entries(author) values (?)',[request.form['searchauthor']])
    db.commit()
    return redirect(url_for('show_entries'))

@app.route('/search_book',methods=['POST'])
def search_book():
    db = get_db()
    db.execute('insert into entries(author) select authors.author from authors inner join authorsbooks on\
                authors.id=authorsbooks.idbook inner join books on authorsbooks.idauthor=books.id \
                where books.book=values(?)',[request.form['searchbook']])
    db.execute('insert into entries(book) values(?)',[request.form['searchbook']])
    db.commit()
    return redirect(url_for('show_entries'))

@app.route('/change_book',methods=['POST'])
def change_book():
    db=get_db()
    db.execute('update books set book=values(?) where book=values(?)',[request.form['newbook']],[request.form['oldbook']])
    db.commit()
    flash('Book was changed')

@app.route('/change_author',methods=['POST'])
def change_author():
    db=get_db()
    db.execute('update authors set author=values(?) where author=values(?)',[request.form['newauthor']],[request.form['oldauthor']])
    db.commit()
    flash('Author was changed')

@app.route('/delete_author',methods=['POST'])
def delete_author():
    db=get_db()
    db.execute('delete from authors where author=values(?)',[request.form['deleteauthor']])
    db.commit()
    flash('Author was deleted')

@app.route('/delete_book',methods=['POST'])
def delete_book():
    db=get_db()
    db.execute('delete from books where book=values(?)',[request.form['deletebook']])
    db.commit()
    flash('Book was deleted')
    
@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        if request.form['username'] != app.config['USERNAME']:
            error = 'Invalid username'
        elif request.form['password'] != app.config['PASSWORD']:
            error = 'Invalid password'
        else:
            session['logged_in'] = True
            flash('You were logged in')
            return redirect(url_for('show_entries'))
    return render_template('login.html', error=error)

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash('You were logged out')
    return redirect(url_for('show_entries'))

if __name__=='__main__':
    init_db()
    app.run()
