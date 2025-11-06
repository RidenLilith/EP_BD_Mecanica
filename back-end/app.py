# backend/app.py
from flask import Flask, request, jsonify
from flask_cors import CORS
from database import Base, engine, SessionLocal
from models import Item

app = Flask(__name__)
CORS(app)

# cria tabelas (em Postgres isso roda na inicialização do container do backend)
Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/api/itens")
def listar_itens():
    db = next(get_db())
    itens = db.query(Item).all()
    return jsonify([{"id": i.id, "nome": i.nome, "descricao": i.descricao} for i in itens])

@app.post("/api/itens")
def criar_item():
    db = next(get_db())
    data = request.get_json(force=True)
    nome = (data.get("nome") or "").strip()
    if not nome:
        return jsonify({"erro": "nome é obrigatório"}), 400
    item = Item(nome=nome, descricao=(data.get("descricao") or "").strip())
    db.add(item)
    db.commit()
    db.refresh(item)
    return jsonify({"id": item.id, "nome": item.nome, "descricao": item.descricao}), 201

@app.put("/api/itens/<int:item_id>")
def atualizar_item(item_id):
    db = next(get_db())
    item = db.query(Item).get(item_id)
    if not item:
        return jsonify({"erro": "não encontrado"}), 404
    data = request.get_json(force=True)
    if "nome" in data:
        item.nome = (data["nome"] or "").strip()
    if "descricao" in data:
        item.descricao = (data["descricao"] or "").strip()
    db.commit()
    return jsonify({"id": item.id, "nome": item.nome, "descricao": item.descricao})

@app.delete("/api/itens/<int:item_id>")
def deletar_item(item_id):
    db = next(get_db())
    item = db.query(Item).get(item_id)
    if not item:
        return jsonify({"erro": "não encontrado"}), 404
    db.delete(item)
    db.commit()
    return "", 204

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
