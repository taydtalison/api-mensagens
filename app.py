from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import SQLAlchemyError

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///mensagens.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Mensagem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(255), nullable=False)

    def to_dict(self):
        return {'id': self.id, 'content': self.content}

@app.before_first_request
def create_tables():
    db.create_all()

@app.route('/mensagens', methods=['GET'])
def get_mensagens():
    try:
        mensagens = Mensagem.query.all()
        return jsonify([m.to_dict() for m in mensagens]), 200
    except SQLAlchemyError as e:
        return jsonify({'error': 'Database error: ' + str(e)}), 500

@app.route('/mensagens', methods=['POST'])
def create_mensagem():
    data = request.get_json()
    if not data or 'content' not in data:
        return jsonify({'error': 'Content is required'}), 400
    content = data['content']
    try:
        mensagem = Mensagem(content=content)
        db.session.add(mensagem)
        db.session.commit()
        return jsonify(mensagem.to_dict()), 201
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({'error': 'Database error: ' + str(e)}), 500

@app.route('/mensagens', methods=['PUT'])
def update_mensagem():
    data = request.get_json()
    if not data or 'id' not in data or 'content' not in data:
        return jsonify({'error': 'Both id and content are required'}), 400
    mensagem = Mensagem.query.get(data['id'])
    if not mensagem:
        return jsonify({'error': 'Mensagem not found'}), 404
    try:
        mensagem.content = data['content']
        db.session.commit()
        return jsonify(mensagem.to_dict()), 200
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({'error': 'Database error: ' + str(e)}), 500

@app.route('/mensagens', methods=['DELETE'])
def delete_mensagem():
    data = request.get_json()
    if not data or 'id' not in data:
        return jsonify({'error': 'Id is required'}), 400
    mensagem = Mensagem.query.get(data['id'])
    if not mensagem:
        return jsonify({'error': 'Mensagem not found'}), 404
    try:
        db.session.delete(mensagem)
        db.session.commit()
        return jsonify({'message': f'Mensagem with id {data["id"]} deleted'}), 200
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({'error': 'Database error: ' + str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)

