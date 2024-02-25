from flask import Flask, request, jsonify
import sqlite3
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test_cases_db.sqlite'
db = SQLAlchemy(app)
migrate = Migrate(app, db)

class TestCase(db.Model):
    __tablename__ = 'test_cases'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(500))

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description
        }

    def __repr__(self):
        return f'<TestCase {self.name}>'


class ExecutionResult(db.Model):
    __tablename__ = 'execution_results'
    id = db.Column(db.Integer, primary_key=True)
    test_case_id = db.Column(db.Integer, db.ForeignKey('test_cases.id'), nullable=False)
    asset_name = db.Column(db.String(100), nullable=False)
    result = db.Column(db.String(500), nullable=False)

    test_case = db.relationship('TestCase', backref=db.backref('execution_results', lazy=True, cascade="all, delete-orphan"))


    def to_dict(self):
        return {
            'id': self.id,
            'test_case_id': self.test_case_id,
            'asset_name': self.asset_name,
            'result': self.result
        }
    def __repr__(self):
        return f'<ExecutionResult {self.asset_name}>'
    




@app.route('/test_cases', methods=['POST'])
def create_test_case():
    data = request.get_json()
    if not data or 'name' not in data:
        return jsonify({"error": "Missing required field 'name' in the request body"}),  400

    try:
        new_test_case = TestCase(name=data['name'], description=data.get('description', None))
        db.session.add(new_test_case)
        db.session.commit()
        return jsonify({"message": "Test case created"}),  201
    except Exception as e:
        db.session.rollback()
        print(f"Exception occurred: {e}")  # This line will print the exception to the console
        return jsonify({"error": "An error occurred while creating the test case"}),  500




@app.route('/test_cases', methods=['GET'])
def get_all_test_cases():
    try:
        test_cases = TestCase.query.all()
        return jsonify([test_case.to_dict() for test_case in test_cases])
    except Exception as e:
        return jsonify({"error": "An error occurred while fetching test cases"}), 500





@app.route('/test_cases/<int:test_case_id>', methods=['GET'])
def get_test_case(test_case_id):
    test_case = TestCase.query.get(test_case_id)
    if not test_case:
        return jsonify({"error": "Test case not found"}), 404
    return jsonify(test_case.to_dict())




@app.route('/test_cases/<int:test_case_id>', methods=['PUT'])
def update_test_case(test_case_id):
    data = request.get_json()
    if not data or 'name' not in data:
        return jsonify({"error": "Missing required field 'name' in the request body"}), 400

    try:
        test_case = TestCase.query.get(test_case_id)
        if not test_case:
            return jsonify({"error": "Test case not found"}), 404
        test_case.name = data['name']
        test_case.description = data.get('description', None)
        db.session.commit()
        return jsonify({"message": "Test case updated"})
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "An error occurred while updating the test case"}), 500




@app.route('/test_cases/<int:test_case_id>', methods=['DELETE'])
def delete_test_case(test_case_id):
    print(1)
    try:
        test_case = db.session.get(TestCase, test_case_id)
        print(2)
        if not test_case:
            print(3)
            return jsonify({"error": "Test case not found"}), 404
        db.session.delete(test_case)
        print(4)
        db.session.commit()
        print(5)
        return jsonify({"message": "Test case deleted"})
    except Exception as e:
        db.session.rollback()
        print(e)
        return jsonify({"error": "An error occurred while deleting the test case"}), 500


@app.route('/execution_results', methods=['POST'])
def create_execution_result():
    data = request.get_json()
    test_case_id = data.get('test_case_id')
    asset_name = data.get('asset_name')
    result = data.get('result')

    new_execution_result = ExecutionResult(test_case_id=test_case_id, asset_name=asset_name, result=result)
    
    db.session.add(new_execution_result)
    db.session.commit()

    return jsonify({'message': 'ExecutionResult created successfully'})


@app.route('/execution_results/<string:asset_name>', methods=['GET'])
def get_execution_results(asset_name):
    try:
        execution_results = ExecutionResult.query.filter_by(asset_name=asset_name).all()
        app.logger.info(f"Query results for {asset_name}: {execution_results}")
        return jsonify([result.to_dict() for result in execution_results])
    except Exception as e:
        return jsonify({"error": "An error occurred while fetching execution results"}), 500
    


if __name__ == '__main__':
    app.run(debug=True)
