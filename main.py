from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///reviews.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'cock'
db = SQLAlchemy(app)

class Review(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    text = db.Column(db.String(500), nullable = False)
    approved = db.Column(db.Boolean, default = False)

class Admin(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String(80), unique=True, nullable = False)
    password_hash = db.Column(db.String(128), nullable = False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

with app.app_context():
    db.create_all()

@app.route('/')
def index():
    reviews = Review.query.filter_by(approved = True).all()
    return render_template('index.html', reviews = reviews)

@app.route('/send', methods=['POST'])
def send():
    review_text = request.form.get('review')
    if review_text:
        new_review = Review(text=review_text)
        db.session.add(new_review)
        db.session.commit()
    return redirect(url_for('index'))

@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if 'admin_id' not in session:
        return redirect(url_for('login'))

    wait_review = Review.query.filter_by(approved = False).all()
    return render_template('admin.html', wait_review = wait_review)

@app.route('/approve/<int:id>')
def approve(id):
    review = Review.query.get(id)
    if review:
        review.approved = True
        db.session.commit()
    return redirect(url_for('admin'))

@app.route('/reject/<int:id>')
def reject(id):
    review = Review.query.get(id)
    if review:
        db.session.delete(review)
        db.session.commit()
    return redirect(url_for('admin'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        admin = Admin.query.filter_by(username = username).first()

        if admin and admin.check_password(password):
            session['admin_id'] = admin.id
            return redirect(url_for('admin'))
        else:
            flash("Неверное имя или пароль", "error")
            return redirect(url_for('login'))

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('admin_id', None)
    return redirect(url_for('login'))

@app.route('/reg', methods=['GET', 'POST'])
def reg():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        adm = Admin.query.filter_by(username = username).first()
        if adm:
            flash('Такой админ уже есть', 'error')
            return redirect(url_for('reg'))
        new_admin = Admin(username = username)
        new_admin.set_password(password)
        db.session.add(new_admin)
        db.session.commit()
        return redirect(url_for('login'))



    return render_template('reg.html')

if __name__ == '__main__':
    app.run(debug = True)