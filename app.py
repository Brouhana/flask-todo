from flask import Flask, render_template, url_for, request, redirect
from flask.globals import request
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///todo.db'
db = SQLAlchemy(app)

class Todo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(300), nullable=False)
    is_important = db.Column(db.Boolean(False), nullable=True)
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
        
    task = Todo.query.get_or_404(id)
    
    try:
        if task.is_important:
            task.is_important = 0
        else:
            task.is_important = 1
    except:
        return render_template('failure.html')

    db.session.commit()
    return redirect('/')
    
if __name__ == "__main__":
    app.run()