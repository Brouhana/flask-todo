from flask import Flask, render_template, url_for, request, redirect
from flask.globals import request
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_migrate import Migrate

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///todo.db'
db = SQLAlchemy(app)
migrate = Migrate(app, db)

class Todo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(300), nullable=False)
    is_important = db.Column(db.Boolean(False), nullable=True)
    is_follow_up = db.Column(db.Boolean(False), nullable=True)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return '<Task %r>' % self.id
    
@app.route('/', methods=['POST', 'GET'])
def index():
    error = False
    
    if request.method == 'POST':
        if not request.form['content']:
            error = True
            return render_template('index.html', error=error)
        
        task_content = request.form['content']
        
        if request.form.get('is_important'): # returns 1 if checkbox is selected
            new_task = Todo(content=task_content, is_important=True)
        else:
            new_task = Todo(content=task_content, is_important=False)
        
        try:
            db.session.add(new_task)
            db.session.commit()
            return redirect('/')
        except:
            return render_template('failure.html')
    else:
        tasks = Todo.query.order_by(Todo.date_created).all()
        return render_template('index.html', tasks=tasks)

@app.route('/complete/<int:id>')
def delete(id):
    delete_task = Todo.query.get_or_404(id)
    
    try:
        db.session.delete(delete_task)
        db.session.commit()
        return redirect('/')
    except:
        return render_template('failure.html')

@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit(id):
    task = Todo.query.get_or_404(id)
    
    if request.method == 'POST':
        task.content = request.form['content']
        
        try:
            db.session.commit()
            return redirect('/')
        except:
            return render_template('failure.html')
    else:
        return render_template('edit.html', task=task)

@app.route('/important/<int:id>')
def mark_important(id):
    task_to_mark = Todo.query.get_or_404(id)
    
    try:
        if task_to_mark.is_important:
            task_to_mark.is_important = 0
        else:
            task_to_mark.is_important = 1
    except:
        return render_template('failure.html')

    db.session.commit()
    return redirect('/')
    
@app.route('/follow-up/<int:id>')
def follow_up(id):
    task_to_follow = Todo.query.get_or_404(id)
    
    try:
        if task_to_follow.is_follow_up:
            task_to_follow.is_follow_up = 0
        else:
            task_to_follow.is_follow_up = 1
    except:
        return render_template('failure.html')
    
    db.session.commit()
    return redirect('/')

@app.route('/tag/important', methods=['GET'])
def important_index():
    tasks = Todo.query.filter_by(is_important='1').all()
    return render_template('important.html', tasks=tasks)

@app.route('/tag/follow-up', methods=['GET'])
def follow_up_index():
    tasks = Todo.query.filter_by(is_follow_up='1').all()
    return render_template('follow-up.html', tasks=tasks)

if __name__ == "__main__":
    app.run()