#!/usr/bin/env python3
"""
Robust seed script for EP_BD_Mecanica.
This file replaces the older, malformed seed.py and provides idempotent
upsert operations that work with Postgres (ON CONFLICT) and SQLite.
"""

from datetime import datetime, timedelta
from sqlalchemy.dialects.postgresql import insert as pg_insert
from database import SessionLocal, Base, engine, DATABASE_URL
from sqlalchemy.exc import OperationalError
from models import (
    Cliente, Servico, Peca, Funcionario, Veiculo, Fornecedor,
    OS, ItemPeca, ItemServico, Pagamento, Agendamento, MovimentoEstoque,
    StatusOS, StatusAgendamento
)

is_postgres = engine.dialect.name == "postgresql"

def mask_url(url: str) -> str:
    try:
        import re
        return re.sub(r':[^:@]+@', ':***@', url)
    except Exception:
        return url

print(f"[seed.py] Engine dialect: {engine.dialect.name} | DB: {mask_url(DATABASE_URL)}")

def upsert_cliente(db, nome, cpf):
    if is_postgres:
        stmt = pg_insert(Cliente.__table__).values(nome_razao=nome, cpf_cnpj=cpf)
        stmt = stmt.on_conflict_do_nothing(index_elements=['cpf_cnpj'])
        db.execute(stmt)
    else:
        if not db.query(Cliente).filter_by(cpf_cnpj=cpf).first():
            db.add(Cliente(nome_razao=nome, cpf_cnpj=cpf))

def upsert_servico(db, desc, preco):
    if is_postgres:
        stmt = pg_insert(Servico.__table__).values(descricao=desc, preco_padrao=preco)
        stmt = stmt.on_conflict_do_nothing(index_elements=['descricao'])
        db.execute(stmt)
    else:
        if not db.query(Servico).filter_by(descricao=desc).first():
            db.add(Servico(descricao=desc, preco_padrao=preco))

def upsert_peca(db, sku, descricao, origem, estoque=0):
    if is_postgres:
        stmt = pg_insert(Peca.__table__).values(sku=sku, descricao=descricao, origem=origem, estoque_atual=estoque)
        stmt = stmt.on_conflict_do_nothing(index_elements=['sku'])
        db.execute(stmt)
    else:
        if not db.query(Peca).filter_by(sku=sku).first():
            db.add(Peca(sku=sku, descricao=descricao, origem=origem, estoque_atual=estoque))

def upsert_funcionario(db, nome, funcao):
    if not db.query(Funcionario).filter_by(nome=nome).first():
        db.add(Funcionario(nome=nome, funcao=funcao))

def upsert_fornecedor(db, nome, cpf=None):
    if cpf:
        if is_postgres:
            stmt = pg_insert(Fornecedor.__table__).values(nome_razao=nome, cpf_cnpj=cpf)
            stmt = stmt.on_conflict_do_nothing(index_elements=['cpf_cnpj'])
            db.execute(stmt)
        else:
            if not db.query(Fornecedor).filter_by(cpf_cnpj=cpf).first():
                db.add(Fornecedor(nome_razao=nome, cpf_cnpj=cpf))
    else:
        if not db.query(Fornecedor).filter_by(nome_razao=nome).first():
            db.add(Fornecedor(nome_razao=nome))

def upsert_veiculo(db, placa, marca, modelo, km_atual, id_cliente):
    if is_postgres:
        stmt = pg_insert(Veiculo.__table__).values(placa=placa, marca=marca, modelo=modelo, km_atual=km_atual, id_cliente=id_cliente)
        stmt = stmt.on_conflict_do_nothing(index_elements=['placa'])
        db.execute(stmt)
    else:
        if not db.query(Veiculo).filter_by(placa=placa).first():
            db.add(Veiculo(placa=placa, marca=marca, modelo=modelo, km_atual=km_atual, id_cliente=id_cliente))

def reset_tables():
    try:
        Base.metadata.drop_all(bind=engine)
        Base.metadata.create_all(bind=engine)
        print("[seed.py] Tables reset OK")
    except OperationalError as e:
        print('[seed.py] ERROR: Unable to reset tables. Check DATABASE_URL and connectivity: ', e)
        raise

def seed():
    try:
        with SessionLocal() as db:
            # CLIENTES
            clientes = [
                ("João da Silva", "123.456.789-00"),
                ("Maria Santos", "987.654.321-11"),
                ("Pedro Oliveira", "456.789.123-22"),
                ("Ana Costa", "789.123.456-33"),
                ("Carlos Souza", "321.654.987-44"),
                ("Oficina XPTO Ltda", "12.345.678/0001-99"),
                ("Transportadora ABC", "98.765.432/0001-88"),
                ("Empresa de Táxi XYZ", "11.222.333/0001-77"),
                ("Auto Escola Rio", "44.555.666/0001-66"),
                ("Frota de Ônibus SP", "55.666.777/0001-55"),
            ]
            for nome, cpf in clientes:
                upsert_cliente(db, nome, cpf)
            db.commit()

            # SERVIÇOS
            servicos = [
                ("Troca de óleo", 120.00),
                ("Alinhamento", 150.00),
                ("Balanceamento", 100.00),
                ("Troca de pneu", 80.00),
            ]
            for desc, preco in servicos:
                upsert_servico(db, desc, preco)
            db.commit()

            # PEÇAS - small sample for speed
            pecas = [
                ("OL-10W40", "Óleo 10W40", "nacional", 50),
                ("VELA-IGN-1", "Vela de ignição padrão", "nacional", 60),
                ("BATE-12V", "Bateria 12V 60Ah", "nacional", 10),
            ]
            for sku, desc, origem, estoque in pecas:
                upsert_peca(db, sku, desc, origem, estoque)
            db.commit()

            # FUNCIONÁRIOS
            funcionarios = [
                ("Pedro Mecânico", "Mecânico"),
                ("Ana Recepção", "Atendimento"),
            ]
            for nome, funcao in funcionarios:
                upsert_funcionario(db, nome, funcao)
            db.commit()

            # FORNECEDORES
            fornecedores = [
                ("Distribuidora Nacional de Peças", "11.111.111/0001-11"),
            ]
            for nome, cpf in fornecedores:
                upsert_fornecedor(db, nome, cpf)
            db.commit()

            # VEÍCULOS
            veiculos = [
                ("ABC-1234", "VW", "Gol", 120000, 1),
            ]
            for placa, marca, modelo, km, id_cliente in veiculos:
                upsert_veiculo(db, placa, marca, modelo, km, id_cliente)
            db.commit()

            # ORDENS (simple example)
            agora = datetime.now()
            oses = []
            for i in range(1, 4):
                os_inst = OS(
                    id_veiculo=1,
                    id_responsavel=1,
                    km_entrada=100000 + (i * 5000),
                    problema_relatado=f"Revisão teste #{i}",
                    status=StatusOS.finalizado if i % 2 == 0 else StatusOS.em_execucao,
                )
                db.add(os_inst)
                db.flush()
                oses.append(os_inst)

                item_serv = ItemServico(id_os=os_inst.id_os, id_servico=1, qtd=1, valor_unit=100.0)
                db.add(item_serv)
                item_peca = ItemPeca(id_os=os_inst.id_os, id_peca=1, qtd=1, valor_unit=50.0)
                db.add(item_peca)
            db.commit()

            # PAGAMENTOS
            for i, os_obj in enumerate(oses, 1):
                pagamento = Pagamento(id_os=os_obj.id_os, data=agora - timedelta(days=i), forma='Dinheiro', valor=200.0 + i)
                db.add(pagamento)
            db.commit()

            # AGENDAMENTOS
            for i in range(1, 4):
                ag = Agendamento(id_cliente=1, id_veiculo=1, id_servico=1, data_hora=agora + timedelta(days=i), status=StatusAgendamento.pendente)
                db.add(ag)
            db.commit()

            # MOVIMENTOS
            for i in range(1, 4):
                mov = MovimentoEstoque(id_peca=1, id_os=oses[0].id_os if oses else None, data=agora, tipo='entrada', origem='Fornecedor', qtd=1, custo_unitario=50.0)
                db.add(mov)
            db.commit()

    except OperationalError as e:
        print('[seed.py] ERROR: Database operation failed, check connection and credentials: ', e)
        raise
    except Exception as e:
        print('[seed.py] ERROR: Seed failed with exception: ', e)
        raise
    else:
        print('✅ Seed completo! Dados de teste inseridos com sucesso.')


if __name__ == '__main__':
    reset_tables()
    seed()
