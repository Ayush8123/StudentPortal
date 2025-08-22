from flask import Flask,render_template,request,redirect,flash,session
from flask_sqlalchemy import SQLAlchemy
import os
from dotenv import load_dotenv #pip install python-dotenv

load_dotenv()
app=Flask(__name__)

# app.secret_key = 'ayushshah8106'  this is not a good practice we should hide this before publishing
app.secret_key = os.getenv('SECRET_KEY')

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///try.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db=SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)

# define model
class student(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    name=db.Column(db.String(100),nullable=False)
    age=db.Column(db.Integer,nullable=False)
    grade=db.Column(db.String(2))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))  #this links student to a user

# Create the table
with app.app_context():
    db.create_all()

@app.route('/')
@app.route('/home')
def home():
    return render_template("index.html")

@app.route('/add', methods=['POST'])
def add():
    if 'user_id' not in session:
        flash("Login first to add students", "warning")
        return redirect('/login')

    name = request.form['name']
    age = request.form['age']
    grade = request.form['grade']
    user_id = session['user_id']

    new_student = student(name=name, age=age, grade=grade, user_id=user_id)
    db.session.add(new_student)
    db.session.commit()

    flash("Student added successfully!", "success")
    return redirect('/home')

# show data
@app.route('/students')
def show():
    if 'user_id' not in session:
        flash("Please login to view your data", "warning")
        return redirect('/login')

    all_stu = student.query.filter_by(user_id=session['user_id']).all()
    return render_template('students.html', student=all_stu)


#  Route: /update/<int:id> — Update student name
@app.route('/update/<int:id>',methods=['GET','POST'])
def update(id):
    s=student.query.get(id)
    s.name=request.form['name']
    db.session.commit() 
    return redirect('/students')

@app.route('/delete/<int:id>',methods=['POST'])
def delete(id):
    s=student.query.get(id)
    db.session.delete(s)
    db.session.commit()
    return redirect('/students')


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        uname = request.form['username']
        pwd = request.form['password']
        existing = User.query.filter_by(username=uname).first()
        if existing:
            flash("Username already exists!", "danger")
        else:
            u = User(username=uname, password=pwd)
            db.session.add(u)
            db.session.commit()
            flash("Signup successful! Please log in.", "success")
            return redirect('/login')
    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        uname = request.form['username']
        pwd = request.form['password']
        u = User.query.filter_by(username=uname, password=pwd).first()
        if u:
            session['user_id'] = u.id
            session['username'] = u.username
            flash("Login successful", "success")
            return redirect('/')
        else:
            flash("Invalid credentials", "danger")
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('username', None)
    flash("Logged out successfully", "info")
    return redirect('/login')


@app.route('/admin')
def admin():
    all_stu=User.query.all()
    return render_template("admin.html",mystu=all_stu)
if __name__=="__main__":
    app.run(debug=True)

import os

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
