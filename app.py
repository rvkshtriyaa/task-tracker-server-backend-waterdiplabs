from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from schemas import TaskSchema
from models import db, Task
import logging

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tasks.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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
        logger.info("Task created: %s", task)
        return task_schema.jsonify(task), 201
    except Exception as e:
        logger.error("Error creating task: %s", e)
        return jsonify({"error": str(e)}), 400

@app.route('/v1/tasks', methods=['GET'])
def list_tasks():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    tasks = Task.query.paginate(page, per_page, error_out=False)
    task_schema = TaskSchema(many=True)
    logger.info("Listing tasks, page %d", page)
    return jsonify({
        'tasks': task_schema.dump(tasks.items),
        'total': tasks.total,
        'page': tasks.page,
        'per_page': tasks.per_page,
    })

@app.route('/v1/tasks/<int:id>', methods=['GET'])
def get_task(id):
    task = Task.query.get(id)
    if task:
        task_schema = TaskSchema()
        logger.info("Task retrieved: %s", task)
        return task_schema.jsonify(task)
    logger.warning("Task not found with id: %d", id)
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
            logger.info("Task updated: %s", updated_task)
            return task_schema.jsonify(updated_task), 200
        except Exception as e:
            logger.error("Error updating task: %s", e)
            return jsonify({"error": str(e)}), 400
    logger.warning("Task not found with id: %d", id)
    return jsonify({"error": "There is no task at that id"}), 404

@app.route('/v1/tasks/<int:id>', methods=['DELETE'])
def delete_task(id):
    task = Task.query.get(id)
    if task:
        db.session.delete(task)
        db.session.commit()
        logger.info("Task deleted with id: %d", id)
        return '', 204
    logger.warning("Task not found with id: %d", id)
    return jsonify({"error": "There is no task at that id"}), 404

if __name__ == '__main__':
    app.run(debug=True)
