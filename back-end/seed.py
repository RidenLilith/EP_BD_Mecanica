# back-end/seed.py
from datetime import datetime, timedelta
from sqlalchemy.dialects.postgresql import insert
from database import SessionLocal, Base, engine
from models import (
    Cliente, Servico, Peca, Funcionario, Veiculo, Fornecedor,
    OS, ItemPeca, ItemServico, Pagamento, Agendamento, MovimentoEstoque,
    StatusOS, StatusAgendamento, OrigemPeca
)

db = SessionLocal()

# ---------- UPSERTS ----------
def upsert_cliente(nome, cpf):
    stmt = insert(Cliente.__table__).values(nome_razao=nome, cpf_cnpj=cpf)
    stmt = stmt.on_conflict_do_nothing(index_elements=['cpf_cnpj'])
    db.execute(stmt)

def upsert_servico(desc, preco):
    stmt = insert(Servico).values(descricao=desc, preco_padrao=preco)
    stmt = stmt.on_conflict_do_nothing(index_elements=['descricao'])
    db.execute(stmt)

def upsert_peca(sku, descricao, origem, estoque=0):
    stmt = insert(Peca.__table__).values(
        sku=sku, descricao=descricao, origem=origem, estoque_atual=estoque
    )
    stmt = stmt.on_conflict_do_nothing(index_elements=['sku'])
    db.execute(stmt)

def upsert_funcionario(nome, funcao):
    stmt = insert(Funcionario.__table__).values(nome=nome, funcao=funcao)
    db.execute(stmt)

def upsert_fornecedor(nome, cpf=None):
    stmt = insert(Fornecedor.__table__).values(nome_razao=nome, cpf_cnpj=cpf)
    if cpf:
        stmt = stmt.on_conflict_do_nothing(index_elements=['cpf_cnpj'])
    db.execute(stmt)

def upsert_veiculo(placa, marca, modelo, km_atual, id_cliente):
    stmt = insert(Veiculo.__table__).values(
        placa=placa,
        marca=marca,
        modelo=modelo,
        km_atual=km_atual,
        id_cliente=id_cliente
    )
    stmt = stmt.on_conflict_do_nothing(index_elements=['placa'])
    db.execute(stmt)

# ---------- RESET TOTAL ----------
def reset_tables():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

# ---------- SEED ----------
def seed():
    # ====== CLIENTES (10) ======
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
        upsert_cliente(nome, cpf)

    # ====== SERVIÇOS (15) ======
    servicos = [
        ("Troca de óleo", 120.00),
        ("Alinhamento", 150.00),
        ("Balanceamento", 100.00),
        ("Troca de pneu", 80.00),
        ("Revisão completa", 300.00),
        ("Troca de pastilha de freio", 200.00),
        ("Limpeza de bico injetor", 180.00),
        ("Troca de bateria", 250.00),
        ("Suspensão e amortecedor", 400.00),
        ("Diagnóstico eletrônico", 150.00),
        ("Troca de correia dentada", 350.00),
        ("Ar condicionado - Limpeza", 220.00),
        ("Troca de velas de ignição", 140.00),
        ("Polimento e enceração", 250.00),
        ("Troca de correntes/correia", 300.00),
    ]
    for desc, preco in servicos:
        upsert_servico(desc, preco)

    # ====== PEÇAS (25) ======
    pecas = [
        ("OL-10W40", "Óleo 10W40", "nacional", 50),
        ("OL-5W30", "Óleo 5W30 sintético", "importada", 30),
        ("FILT-AR-FOX", "Filtro de ar FOX", "importada", 20),
        ("FILT-AR-VW", "Filtro de ar VW Gol", "nacional", 25),
        ("FILT-OLEO-1", "Filtro de óleo padrão", "nacional", 40),
        ("FILT-OLEO-IMP", "Filtro de óleo importado", "importada", 15),
        ("PAST-FREIO-1", "Pastilha de freio dianteira", "nacional", 35),
        ("PAST-FREIO-2", "Pastilha de freio traseira", "importada", 20),
        ("BATE-12V", "Bateria 12V 60Ah", "nacional", 10),
        ("BATE-12V-PLUS", "Bateria Premium 12V 70Ah", "importada", 8),
        ("VELA-IGN-1", "Vela de ignição padrão", "nacional", 60),
        ("VELA-IGN-IMP", "Vela de ignição iridium", "importada", 25),
        ("AMORT-DEF", "Amortecedor dianteiro", "nacional", 12),
        ("AMORT-TRAS", "Amortecedor traseiro", "importada", 10),
        ("CORREIA-1", "Correia dentada 1.8", "nacional", 8),
        ("CORREIA-2", "Correia dentada 2.0", "importada", 5),
        ("PNEU-185", "Pneu 185/65R15", "importada", 18),
        ("PNEU-205", "Pneu 205/55R16", "importada", 14),
        ("DISCO-FREIO", "Disco de freio ventilado", "nacional", 16),
        ("CILINDRO-MESTRE", "Cilindro mestre de freio", "importada", 6),
        ("JOGO-CORRENTE", "Jogo de corrente completo", "nacional", 5),
        ("SENSOR-LAMBDA", "Sensor lambda O2", "importada", 12),
        ("BOBINA-IGNIÇÃO", "Bobina de ignição", "nacional", 20),
        ("RADIADOR", "Radiador de alumínio", "importada", 4),
        ("EMBREAGEM-KIT", "Kit embreagem completo", "importada", 3),
    ]
    for sku, desc, origem, estoque in pecas:
        upsert_peca(sku, desc, origem, estoque)

    # ====== FUNCIONÁRIOS (8) ======
    funcionarios = [
        ("Pedro Mecânico", "Mecânico"),
        ("Ana Recepção", "Atendimento"),
        ("Carlos Silva", "Mecânico de motor"),
        ("Rodrigo Suspensão", "Especialista em suspensão"),
        ("Fabio Elétrica", "Eletricista automotivo"),
        ("Mariana Gerente", "Gerente de oficina"),
        ("João Pintor", "Pintor automotivo"),
        ("Lucas Assistente", "Assistente de oficina"),
    ]
    for nome, funcao in funcionarios:
        upsert_funcionario(nome, funcao)

    # ====== FORNECEDORES (8) ======
    fornecedores = [
        ("Distribuidora Nacional de Peças", "11.111.111/0001-11"),
        ("Importadora Turbo Parts", "22.222.222/0001-22"),
        ("Bosch Brasil", "33.333.333/0001-33"),
        ("Valeo Componentes", "44.444.444/0001-44"),
        ("Continental Pneus", "55.555.555/0001-55"),
        ("ZF Sachs Suspensão", "66.666.666/0001-66"),
        ("Feuling Importações", "77.777.777/0001-77"),
        ("Pirelli do Brasil", "88.888.888/0001-88"),
    ]
    for nome, cpf in fornecedores:
        upsert_fornecedor(nome, cpf)

    # ====== VEÍCULOS (12) ======
    veiculos = [
        ("ABC-1234", "VW", "Gol", 120000, 1),
        ("DEF-5678", "Honda", "CG 160", 35000, 1),
        ("XYZ-9999", "Fiat", "Strada", 80000, 2),
        ("GHI-2020", "Toyota", "Corolla", 95000, 3),
        ("JKL-3030", "Ford", "Ka", 110000, 4),
        ("MNO-4040", "Hyundai", "HB20", 65000, 5),
        ("PQR-5050", "Chevrolet", "Onix", 75000, 6),
        ("STU-6060", "Renault", "Sandero", 85000, 7),
        ("VWX-7070", "Volkswagen", "Up", 45000, 8),
        ("YZA-8080", "Fiat", "Mobi", 40000, 9),
        ("BCD-9090", "Chevrolet", "S10", 160000, 10),
        ("EFG-1111", "Iveco", "Daily", 220000, 10),
    ]
    for placa, marca, modelo, km, id_cliente in veiculos:
        upsert_veiculo(placa, marca, modelo, km, id_cliente)

    db.commit()

    # ====== ORDENS DE SERVIÇO (10) com ItemPeca e ItemServico ======
    agora = datetime.now()
    oses = []
    
    for i in range(1, 11):
        os = OS(
            id_veiculo=((i - 1) % 12) + 1,  # Distribui entre 12 veículos
            id_responsavel=((i - 1) % 8) + 1,  # Distribui entre 8 funcionários
            km_entrada=100000 + (i * 5000),
            problema_relatado=f"Problemas no serviço #{i}: revisão geral/troca de óleo/diagnóstico",
            status=StatusOS.finalizado if i <= 7 else StatusOS.em_execucao,
        )
        db.add(os)
        db.flush()
        oses.append(os)
        
        # Adiciona 1-3 serviços por OS
        num_servicos = (i % 3) + 1
        for j in range(1, num_servicos + 1):
            servico_id = ((i + j - 2) % 15) + 1
            item_serv = ItemServico(
                id_os=os.id_os,
                id_servico=servico_id,
                qtd=1,
                valor_unit=100.00 + (i * 10)
            )
            db.add(item_serv)
        
        # Adiciona 1-3 peças por OS
        num_pecas = (i % 3) + 1
        for j in range(1, num_pecas + 1):
            peca_id = ((i + j - 1) % 25) + 1
            item_peca = ItemPeca(
                id_os=os.id_os,
                id_peca=peca_id,
                qtd=(j % 3) + 1,
                valor_unit=50.00 + (i * 5)
            )
            db.add(item_peca)

    db.commit()

    # ====== PAGAMENTOS (10) - um por OS ======
    for i, os in enumerate(oses, 1):
        pagamento = Pagamento(
            id_os=os.id_os,
            data=agora - timedelta(days=30 - i + 2),
            forma="Cartão débito" if i % 3 == 0 else ("Dinheiro" if i % 3 == 1 else "Cartão crédito"),
            valor=500.00 + (i * 50)
        )
        db.add(pagamento)

    db.commit()

    # ====== AGENDAMENTOS (12) ======
    for i in range(1, 13):
        agendamento = Agendamento(
            id_cliente=((i - 1) % 10) + 1,
            id_veiculo=((i - 1) % 12) + 1,
            id_servico=((i - 1) % 15) + 1,
            data_hora=agora + timedelta(days=i, hours=10),
            status=StatusAgendamento.confirmado if i % 2 == 0 else StatusAgendamento.pendente
        )
        db.add(agendamento)

    db.commit()

    # ====== MOVIMENTOS DE ESTOQUE (15) ======
    for i in range(1, 16):
        os_id = (i % 10) + 1 if i <= 10 else None
        movimento = MovimentoEstoque(
            id_peca=((i - 1) % 25) + 1,
            id_os=os_id,
            data=agora - timedelta(days=20 - i),
            tipo="saida" if i % 2 == 0 else "entrada",
            origem="Fornecedor" if i % 2 == 0 else "Devolução",
            qtd=i,
            custo_unitario=50.00 + (i * 5)
        )
        db.add(movimento)

    db.commit()
    print("✅ Seed completo! Dados de teste inseridos com sucesso.")

if __name__ == "__main__":
    reset_tables()
    seed()
