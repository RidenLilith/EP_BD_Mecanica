# --- IMPORTS ESSENCIAIS (adicione no topo do app.py) ---
import os, sys
from datetime import datetime

# garante que dá pra importar database.py / models.py quando rodar fora do Docker
sys.path.append(os.path.dirname(__file__))

from flask import Flask, request, jsonify
from flask_cors import CORS
from sqlalchemy import func, and_

from database import Base, engine, SessionLocal
from sqlalchemy.exc import OperationalError
from models import (
    Cliente, Veiculo, Funcionario, Servico, Peca,
    OS, ItemPeca, ItemServico, Pagamento,
    Agendamento, StatusAgendamento, StatusOS, OrigemPeca,
    Fornecedor, MovimentoEstoque  # <<< ADICIONADOS
)

app = Flask(__name__)
CORS(app)

def db_sess():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# -------- Listagens simples --------
@app.get("/api/pecas")
def listar_pecas():
    db = next(db_sess())
    rows = db.query(Peca).order_by(Peca.descricao).all()
    return jsonify([{
        "id_peca": p.id_peca, "sku": p.sku, "descricao": p.descricao,
        "origem": p.origem.value, "estoque_atual": p.estoque_atual
    } for p in rows])

@app.get("/api/funcionarios")
def listar_funcionarios():
    db = next(db_sess())
    rows = db.query(Funcionario).order_by(Funcionario.nome).all()
    return jsonify([{"id_funcionario": f.id_funcionario, "nome": f.nome, "funcao": f.funcao} for f in rows])

@app.get("/api/clientes")
def listar_clientes():
    db = next(db_sess())
    rows = db.query(Cliente).order_by(Cliente.nome_razao).all()
    return jsonify([{"id_cliente": c.id_cliente, "nome_razao": c.nome_razao, "cpf_cnpj": c.cpf_cnpj} for c in rows])

@app.get("/api/veiculos")
def listar_veiculos():
    db = next(db_sess())
    rows = db.query(Veiculo).order_by(Veiculo.placa).all()
    return jsonify([{
        "id_veiculo": v.id_veiculo, "placa": v.placa, "marca": v.marca, "modelo": v.modelo,
        "cliente": {"id": v.cliente.id_cliente, "nome": v.cliente.nome_razao}
    } for v in rows])

@app.post("/api/veiculos")
def criar_veiculo():
    db = next(db_sess())
    data = request.get_json(force=True)

    placa = (data.get("placa") or "").strip().upper()
    id_cliente = data.get("id_cliente")

    if not placa or not id_cliente:
        return jsonify({"erro": "placa e id_cliente são obrigatórios"}), 400

    # Verifica se cliente existe
    cliente = db.query(Cliente).get(id_cliente)
    if not cliente:
        return jsonify({"erro": "cliente não encontrado"}), 404

    # Garante placa única
    ja_existe = db.query(Veiculo).filter_by(placa=placa).first()
    if ja_existe:
        return jsonify({"erro": "já existe veículo com essa placa"}), 409

    v = Veiculo(
        placa=placa,
        chassi=(data.get("chassi") or "").strip(),
        km_atual=data.get("km_atual") or 0,
        marca=(data.get("marca") or "").strip(),
        modelo=(data.get("modelo") or "").strip(),
        id_cliente=id_cliente,
    )
    db.add(v)
    db.commit()
    db.refresh(v)

    return jsonify({
        "id_veiculo": v.id_veiculo,
        "placa": v.placa,
        "marca": v.marca,
        "modelo": v.modelo,
        "km_atual": v.km_atual,
        "cliente": {
            "id": v.cliente.id_cliente,
            "nome": v.cliente.nome_razao
        }
    }), 201


@app.get("/api/servicos")
def listar_servicos():
    db = next(db_sess())
    rows = db.query(Servico).order_by(Servico.descricao).all()
    return jsonify([{"id_servico": s.id_servico, "descricao": s.descricao, "preco_padrao": str(s.preco_padrao or 0)} for s in rows])

# -------- (3.1) Peças danificadas por veículo + origem --------
# GET /api/relatorios/pecas-danificadas?veiculo_id=123
@app.get("/api/relatorios/pecas-danificadas")
def pecas_danificadas_por_veiculo():
    veiculo_id = request.args.get("veiculo_id", type=int)
    if not veiculo_id:
        return jsonify({"erro": "informe veiculo_id"}), 400
    db = next(db_sess())

    # Une OS -> ItemPeca -> Peca; agrupa por peça/origem e soma qtd
    q = (
        db.query(
            Peca.id_peca, Peca.descricao, Peca.origem, func.sum(ItemPeca.qtd).label("qtd_total")
        )
        .join(ItemPeca, ItemPeca.id_peca == Peca.id_peca)
        .join(OS, OS.id_os == ItemPeca.id_os)
        .filter(OS.id_veiculo == veiculo_id)
        .group_by(Peca.id_peca, Peca.descricao, Peca.origem)
        .order_by(Peca.descricao)
    )
    data = [{
        "id_peca": r.id_peca,
        "descricao": r.descricao,
        "origem": r.origem.value,
        "qtd_total": int(r.qtd_total)
    } for r in q.all()]

    return jsonify({"veiculo_id": veiculo_id, "pecas_para_troca": data})

# -------- (3.2) Agendar serviço (evita conflito de horário) --------
# GET /api/agendamentos
@app.get("/api/agendamentos")
def listar_agendamentos():
    db = next(db_sess())
    ags = (
        db.query(Agendamento)
        .order_by(Agendamento.data_hora.desc())
        .all()
    )

    resp = []
    for a in ags:
        resp.append({
            "id_agendamento": a.id_agendamento,
            "data_hora": a.data_hora.isoformat() if a.data_hora else None,
            "status": a.status.value,
            "cliente": a.cliente.nome_razao if a.cliente else "",
            "veiculo": f"{a.veiculo.placa} — {a.veiculo.marca} {a.veiculo.modelo}" if a.veiculo else "",
            "servico": a.servico.descricao if a.servico else "",
        })
    return jsonify(resp)


# POST /api/agendamentos
@app.post("/api/agendamentos")
def criar_agendamento():
    db = next(db_sess())
    payload = request.get_json(force=True) or {}

    try:
        id_cliente = int(payload["id_cliente"])
        id_veiculo = int(payload["id_veiculo"])
        id_servico = int(payload["id_servico"])
        data_str   = payload["data_hora"]

        # Normaliza datetime-local do HTML (YYYY-MM-DDTHH:MM)
        if isinstance(data_str, str):
            if len(data_str) == 16:            # 2025-12-22T18:30
                data_str += ":00"
            data_hora = datetime.fromisoformat(data_str)
        else:
            data_hora = data_str

    except Exception:
        return jsonify({
            "erro": "JSON inválido. Campos obrigatórios: id_cliente, id_veiculo, id_servico, data_hora ISO"
        }), 400

    # Confere se o veículo pertence ao cliente
    veic = db.query(Veiculo).get(id_veiculo)
    if not veic or veic.id_cliente != id_cliente:
        return jsonify({"erro": "veículo não pertence ao cliente informado"}), 400

    # Conflito de horário (mesmo veículo, mesma data/hora, ignorando cancelados)
    conflito = db.query(Agendamento).filter(
        Agendamento.id_veiculo == id_veiculo,
        Agendamento.data_hora == data_hora,
        Agendamento.status != StatusAgendamento.cancelado
    ).first()

    if conflito:
        return jsonify({"erro": "conflito de horário para este veículo"}), 409

    novo = Agendamento(
        id_cliente=id_cliente,
        id_veiculo=id_veiculo,
        id_servico=id_servico,
        data_hora=data_hora
    )
    db.add(novo)
    db.commit()
    db.refresh(novo)

    return jsonify({
        "id_agendamento": novo.id_agendamento,
        "status": novo.status.value
    }), 201

@app.get("/api/clientes/<int:id_cliente>/veiculos")
def listar_veiculos_de_cliente(id_cliente):
    db = next(db_sess())

    # garante que o cliente existe
    cliente = db.query(Cliente).get(id_cliente)
    if not cliente:
        return jsonify({"erro": "cliente não encontrado"}), 404

    veiculos = (
        db.query(Veiculo)
        .filter(Veiculo.id_cliente == id_cliente)
        .order_by(Veiculo.placa)
        .all()
    )

    return jsonify([
        {
            "id": v.id_veiculo,
            "placa": v.placa,
            "marca": v.marca,
            "modelo": v.modelo,
        }
        for v in veiculos
    ])



def criar_agendamento():
    db = next(db_sess())
    payload = request.get_json(force=True) or {}

    try:
        # Campos obrigatórios
        id_cliente = int(payload["id_cliente"])
        id_veiculo = int(payload["id_veiculo"])
        id_servico = int(payload["id_servico"])
        data_str   = payload["data_hora"]

        # Normaliza datetime-local do HTML (YYYY-MM-DDTHH:MM ou com segundos)
        if isinstance(data_str, str):
            if len(data_str) == 16:        # 2025-12-22T18:30
                data_str = data_str + ":00"
            data_hora = datetime.fromisoformat(data_str)
        else:
            data_hora = data_str

    except Exception:
        return jsonify({
            "erro": "JSON inválido. Campos obrigatórios: id_cliente, id_veiculo, id_servico, data_hora ISO"
        }), 400

    # Confere se veículo realmente pertence a esse cliente (coerência extra)
    veic = db.query(Veiculo).get(id_veiculo)
    if not veic or veic.id_cliente != id_cliente:
        return jsonify({"erro": "veículo não pertence ao cliente informado"}), 400

    # Conflito simples: mesmo veículo no mesmo horário (ignorando cancelados)
    conflito = db.query(Agendamento).filter(
        Agendamento.id_veiculo == id_veiculo,
        Agendamento.data_hora == data_hora,
        Agendamento.status != StatusAgendamento.cancelado
    ).first()

    if conflito:
        return jsonify({"erro": "conflito de horário para este veículo"}), 409

    # Cria de fato o agendamento
    novo = Agendamento(
        id_cliente=id_cliente,
        id_veiculo=id_veiculo,
        id_servico=id_servico,
        data_hora=data_hora
    )
    db.add(novo)
    db.commit()
    db.refresh(novo)

    return jsonify({
        "id_agendamento": novo.id_agendamento,
        "status": novo.status.value
    }), 201

# -------- (3.3) Histórico de manutenção por veículo --------
# GET /api/relatorios/historico-veiculo?veiculo_id=123
@app.get("/api/relatorios/historico-veiculo")
def historico_por_veiculo():
    veiculo_id = request.args.get("veiculo_id", type=int)
    if not veiculo_id:
        return jsonify({"erro": "informe veiculo_id"}), 400
    db = next(db_sess())

    ordens = (
        db.query(OS)
        .filter(OS.id_veiculo == veiculo_id)
        .order_by(OS.id_os.desc())
        .all()
    )
    resp = []
    for os in ordens:
        servs = [{
            "servico": it.servico.descricao,
            "qtd": it.qtd,
            "valor_unit": str(it.valor_unit or 0)
        } for it in os.itens_servico]
        pecs = [{
            "peca": it.peca.descricao,
            "origem": it.peca.origem.value,
            "qtd": it.qtd,
            "valor_unit": str(it.valor_unit or 0)
        } for it in os.itens_peca]
        pagtos = [{
            "data": p.data.isoformat() if p.data else None,
            "forma": p.forma,
            "valor": str(p.valor)
        } for p in os.pagamentos]
        resp.append({
            "id_os": os.id_os,
            "status": os.status.value,
            "km_entrada": os.km_entrada,
            "problema_relatado": os.problema_relatado,
            "servicos": servs,
            "pecas": pecs,
            "pagamentos": pagtos,
            "responsavel": os.responsavel.nome
        })
    return jsonify({"veiculo_id": veiculo_id, "ordens": resp})

# Listar fornecedores
@app.get("/api/fornecedores")
def listar_fornecedores():
    db = next(db_sess())
    rows = db.query(Fornecedor).order_by(Fornecedor.nome_razao).all()
    return jsonify([{
        "id_fornecedor": f.id_fornecedor,
        "nome_razao": f.nome_razao,
        "cpf_cnpj": f.cpf_cnpj
    } for f in rows])

# Listar movimentos de estoque (com filtros opcionais)
# /api/movimentos-estoque?os_id=1&id_peca=3
@app.get("/api/movimentos-estoque")
def listar_movimentos():
    db = next(db_sess())
    q = db.query(MovimentoEstoque).order_by(MovimentoEstoque.data.desc())
    os_id = request.args.get("os_id", type=int)
    peca_id = request.args.get("id_peca", type=int)
    if os_id:
        q = q.filter(MovimentoEstoque.id_os == os_id)
    if peca_id:
        q = q.filter(MovimentoEstoque.id_peca == peca_id)
    rows = q.all()
    return jsonify([{
        "id_movimento": m.id_movimento,
        "data": m.data.isoformat(),
        "tipo": m.tipo.value,
        "origem": m.origem,
        "qtd": m.qtd,
        "custo_unitario": str(m.custo_unitario) if m.custo_unitario is not None else None,
        "id_os": m.id_os,
        "peca": {
            "id_peca": m.peca.id_peca,
            "descricao": m.peca.descricao
        }
    } for m in rows])

@app.post("/api/clientes")
def criar_cliente():
    db = next(db_sess())
    dados = request.get_json()
    cli = Cliente(nome_razao=dados["nome_razao"], cpf_cnpj=dados["cpf_cnpj"])
    db.add(cli)
    db.commit()
    db.refresh(cli)
    return jsonify({"id_cliente": cli.id_cliente}), 201

@app.post("/api/funcionarios")
def criar_funcionario():
    db = next(db_sess())
    d = request.get_json()
    f = Funcionario(nome=d["nome"], funcao=d.get("funcao"))
    db.add(f); db.commit(); db.refresh(f)
    return jsonify({"id_funcionario": f.id_funcionario}), 201

@app.post("/api/servicos")
def criar_servico():
    db = next(db_sess())
    d = request.get_json()
    s = Servico(descricao=d["descricao"], preco_padrao=d.get("preco_padrao"))
    db.add(s); db.commit(); db.refresh(s)
    return jsonify({"id_servico": s.id_servico}), 201

@app.post("/api/pecas")
def criar_peca():
    db = next(db_sess())
    d = request.get_json()
    p = Peca(
        sku=d["sku"], descricao=d["descricao"],
        origem=d["origem"], estoque_atual=d.get("estoque_atual", 0)
    )
    db.add(p); db.commit(); db.refresh(p)
    return jsonify({"id_peca": p.id_peca}), 201

@app.post("/api/fornecedores")
def criar_fornecedor():
    db = next(db_sess())
    d = request.get_json()
    f = Fornecedor(nome_razao=d["nome_razao"], cpf_cnpj=d.get("cpf_cnpj"))
    db.add(f); db.commit(); db.refresh(f)
    return jsonify({"id_fornecedor": f.id_fornecedor}), 201


if __name__ == "__main__":
    # Print connection info so users know what's being used
    try:
        from database import DATABASE_URL
        masked = DATABASE_URL
        try:
            # mask password if present
            import re
            masked = re.sub(r':[^:@]+@', ':***@', masked)
        except Exception:
            pass
        print(f"[app.py] Starting app with DATABASE_URL: {masked}")
    except Exception:
        pass
    app.run(host="0.0.0.0", port=5000, debug=True)

@app.get('/api/health')
def health_check():
    # simple healthcheck: app ok and try a DB query
    status = {"app": True, "db": False}
    try:
        db = next(db_sess())
        db.execute("SELECT 1")
        status['db'] = True
    except Exception:
        status['db'] = False
    finally:
        try:
            db.close()
        except Exception:
            pass
    return jsonify(status)

