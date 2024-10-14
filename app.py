from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from schemas import TaskSchema
from models import db, Task

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tasks.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

@app.before_first_request
def create_tables():
    db.create_all()

@app.route('/v1/tasks', methods=['POST'])
def create_task():
    data = request.json
    task_schema = TaskSchema()
    try:
        task = task_schema.load(data)
        db.session.add(task)
        db.session.commit()
        return task_schema.jsonify(task), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route('/v1/tasks', methods=['GET'])
def list_tasks():
    tasks = Task.query.all()
    task_schema = TaskSchema(many=True)
    return task_schema.jsonify(tasks)

@app.route('/v1/tasks/<int:id>', methods=['GET'])
def get_task(id):
    task = Task.query.get(id)
    if task:
        task_schema = TaskSchema()
        return task_schema.jsonify(task)
    return jsonify({"error": "There is no task at that id"}), 404

@app.route('/v1/tasks/<int:id>', methods=['PUT'])
def update_task(id):
    task = Task.query.get(id)
    if task:
        data = request.json
        task_schema = TaskSchema()
        try:
            updated_task = task_schema.load(data, instance=task)
            db.session.commit()
            return task_schema.jsonify(updated_task), 200
        except Exception as e:
            return jsonify({"error": str(e)}), 400
    return jsonify({"error": "There is no task at that id"}), 404

@app.route('/v1/tasks/<int:id>', methods=['DELETE'])
def delete_task(id):
    task = Task.query.get(id)
    if task:
        db.session.delete(task)
        db.session.commit()
        return '', 204
    return jsonify({"error": "There is no task at that id"}), 404

if __name__ == '__main__':
    app.run(debug=True)
