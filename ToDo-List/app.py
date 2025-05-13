from flask import Flask, render_template, request, redirect, url_for, jsonify
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///todo.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # Отключаем предупреждение
db = SQLAlchemy(app)

class Task(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    title = db.Column(db.String(100), nullable = False)
    is_completed = db.Column(db.Boolean, default = False)

# Главная страница с задачами
@app.route('/')
def index():
    tasks = Task.query.all()
    return render_template('index.html', tasks=tasks)

# Добавление задачи
@app.route('/add',methods=['POST'])
def add_task():
    title = request.form['title']
    if title == "":
        return redirect(url_for('index'))
    new_task = Task(title=title)
    db.session.add(new_task)
    db.session.commit()
    return redirect(url_for('index'))

# Выполнение задачи
@app.route('/toggle/<int:id>')
def toggle_task(id):
    task = Task.query.get(id)
    task.is_completed = True
    db.session.commit()
    return redirect(url_for('index'))

# Удаление задачи
@app.route('/delete/<int:id>')
def delete_task(id):
    task = Task.query.get(id)
    db.session.delete(task)
    db.session.commit()
    return redirect(url_for('index'))

# REST API
@app.route('/api/tasks', methods=['GET'])
def get_tasks_api():
    tasks = Task.query.all()
    return jsonify([{
        'id': t.id,
        'title': t.title,
        'is_completed': t.is_completed
    } for t in tasks])

@app.route('/api/tasks', methods=['POST'])
def add_tasks_api():
    data = request.get_json()
    if data['title'] == "":
        return jsonify({ 'status': 'not created, empty title'}), 422
    new_task = Task(title=data['title'])
    db.session.add(new_task)
    db.session.commit()
    return jsonify({ 'id': new_task.id }), 201

@app.route('/api/tasks/<int:id>', methods=['PUT'])
def toggle_tasks_api(id):
    task = Task.query.get(id)
    task.is_completed = True
    db.session.commit()
    return jsonify({ 'is_completed': task.is_completed})

@app.route('/api/tasks/<int:id>', methods=['DELETE'])
def delete_tasks_api(id):
    task = Task.query.get(id)
    db.session.delete(task)
    db.session.commit()
    return jsonify({ 'status': 'deleted'})

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)