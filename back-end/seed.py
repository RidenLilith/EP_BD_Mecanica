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

                ("Juliana Pereira", "222.111.444-55"),
                ("Marcelo Andrade", "333.222.111-66"),
                ("Fernanda Barros", "444.333.222-77"),
                ("Gustavo Ribeiro", "555.444.333-88"),
                ("Patrícia Mendes", "666.555.444-99"),

                ("Mercado Central Ltda", "22.111.333/0001-44"),
                ("Construtora Alpha", "33.222.444/0001-55"),
                ("Auto Peças Brasília", "44.333.555/0001-66"),
                ("Serviços Rápidos ME", "55.444.666/0001-77"),
                ("GlassCar Vidros", "66.555.777/0001-88"),

                ("Eduardo Lima", "111.888.999-77"),
                ("Sofia Martins", "222.777.888-66"),
                ("Roberto Farias", "333.666.777-55"),
                ("Daniel Rodrigues", "444.555.666-44"),
                ("Helena Cardoso", "555.444.555-33"),
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
                ("OL-10W40", "Óleo 10W40 (Lubrificante de Motor)", "nacional", 50),
                ("VELA-IGN-1", "Vela de Ignição Padrão", "nacional", 60),
                ("BATE-12V60", "Bateria 12V 60Ah", "nacional", 10),
                ("FILT-AR-01", "Filtro de Ar", "nacional", 40),
                ("FILT-COMB-02", "Filtro de Combustível", "nacional", 35),

                ("FILT-OL-03", "Filtro de Óleo", "nacional", 55),
                ("PAST-FRE-01", "Pastilha de Freio Dianteira", "importada", 30),
                ("PARA-LAMP-H7", "Lâmpada Automotiva H7", "nacional", 80),
                ("AMORT-DI-01", "Amortecedor Dianteiro", "importada", 20),
                ("AMORT-TR-01", "Amortecedor Traseiro", "importada", 18),

                ("CORR-DENT-01", "Correia Dentada", "nacional", 25),
                ("CORR-ALT-02", "Correia do Alternador", "nacional", 40),
                ("PNEU-ARO14-01", "Pneu Aro 14", "importada", 15),
                ("PNEU-ARO15-02", "Pneu Aro 15", "importada", 12),
                ("ROD-ALUM-01", "Roda de Alumínio Aro 15", "importada", 8),

                ("DISCO-FRE-01", "Disco de Freio", "nacional", 33),
                ("KIT-EMB-01", "Kit de Embreagem", "importada", 14),
                ("JUNT-CAB-01", "Junta do Cabeçote", "nacional", 22),
                ("BOMBA-COMB-01", "Bomba de Combustível", "importada", 9),
                ("BOMBA-AGUA-01", "Bomba d’Água", "nacional", 17),

                ("SENSOR-MAP-01", "Sensor MAP", "nacional", 26),
                ("SENSOR-LAMB-01", "Sensor de Oxigênio (Lambda)", "importada", 19),
                ("MOTOR-ARR-01", "Motor de Partida", "importada", 7),
                ("ALTERNADOR-01", "Alternador", "importada", 6),
                ("RADIADOR-01", "Radiador", "importada", 11)
            ]

            for sku, desc, origem, estoque in pecas:
                upsert_peca(db, sku, desc, origem, estoque)
            db.commit()

            # FUNCIONÁRIOS
            funcionarios = [
                ("Pedro Mecânico", "Mecânico"),
                ("Ana Recepção", "Atendimento"),
                ("João Torres", "Mecânico"),
                ("Marcos Almeida", "Mecânico"),
                ("Juliana Prado", "Atendimento"),
                ("Fernanda Lopes", "Gerente"),
                ("Carlos Moreira", "Eletricista"),
                ("Tiago Guerra", "Mecânico"),
                ("Rafael Duarte", "Mecânico"),
                ("Patrícia Lima", "Atendimento"),

                ("Bruno Mendes", "Mecânico"),
                ("Camila Rocha", "Financeiro"),
                ("Leonardo Martins", "Mecânico"),
                ("Larissa Queiroz", "Atendimento"),
                ("Gustavo Amaral", "Supervisor"),

                ("Cláudio Ferreira", "Mecânico"),
                ("Beatriz Ribeiro", "Atendimento"),
                ("Renato Cardoso", "Mecânico"),
                ("Simone Garcia", "Financeiro"),
                ("Eduardo Vaz", "Eletricista"),

                ("Lucas Antunes", "Mecânico"),
                ("Viviane Sales", "Gerente"),
                ("Roberta Neves", "Atendimento"),
                ("Henrique Ramos", "Mecânico"),
                ("Mateus Silveira", "Mecânico")
            ]
            for nome, funcao in funcionarios:
                upsert_funcionario(db, nome, funcao)
            db.commit()
            for nome, funcao in funcionarios:
                upsert_funcionario(db, nome, funcao)
            db.commit()

            # FORNECEDORES
            fornecedores = [
                ("Distribuidora Nacional de Peças", "11.111.111/0001-11"),
                ("Auto Peças Brasil Ltda", "22.222.222/0001-22"),
                ("Mundial AutoParts", "33.333.333/0001-33"),
                ("FornecMax Auto", "44.444.444/0001-44"),
                ("TurboCar Importados", "55.555.555/0001-55"),

                ("Metalúrgica São Carlos", "66.666.666/0001-66"),
                ("AutoTech Componentes", "77.777.777/0001-77"),
                ("Grupo PeçAuto SP", "88.888.888/0001-88"),
                ("Comercial AutoNorte", "99.999.999/0001-99"),
                ("CenterCar Distribuições", "10.101.010/0001-10"),

                ("MecParts Solutions", "20.202.020/0001-20"),
                ("Importadora SpeedParts", "30.303.030/0001-30"),
                ("Premium AutoStore", "40.404.040/0001-40"),
                ("MasterPeças Industrial", "50.505.050/0001-50"),
                ("MegaTorque Auto", "60.606.060/0001-60"),

                ("AutoLine Distribuidora", "70.707.070/0001-70"),
                ("TopGear Comércio Automotivo", "80.808.080/0001-80"),
                ("CityCar Suprimentos", "90.909.090/0001-90"),
                ("FastParts Mercantil", "12.121.212/0001-12"),
                ("União Auto Ltda", "23.232.323/0001-23"),

                ("Prime Importadora Automotiva", "34.343.434/0001-34"),
                ("Delta Auto Fornecimentos", "45.454.545/0001-45"),
                ("Omega Auto Supply", "56.565.656/0001-56"),
                ("V8 Componentes Automotivos", "67.676.767/0001-67"),
                ("Autocenter Global", "78.787.878/0001-78"),
            ]

            for nome, cpf in fornecedores:
                upsert_fornecedor(db, nome, cpf)
            db.commit()


            # VEÍCULOS
            veiculos = [
                ("ABC-1234", "VW", "Gol", 120000, 1),
                ("DEF-5678", "Fiat", "Uno", 90000, 2),
                ("GHI-9101", "Chevrolet", "Onix", 45000, 3),
                ("JKL-1213", "Hyundai", "HB20", 30000, 4),
                ("MNO-1415", "Ford", "Ka", 80000, 5),

                ("PQR-1617", "Renault", "Clio", 110000, 6),
                ("STU-1819", "Peugeot", "208", 60000, 7),
                ("VWX-2021", "Toyota", "Corolla", 70000, 8),
                ("YZA-2223", "Honda", "Civic", 55000, 9),
                ("BCD-2425", "VW", "Polo", 35000, 10),

                ("EFG-2627", "Fiat", "Argo", 40000, 11),
                ("HIJ-2829", "Chevrolet", "Prisma", 75000, 12),
                ("KLM-3031", "Hyundai", "Creta", 50000, 13),
                ("NOP-3233", "Ford", "Ranger", 95000, 14),
                ("QRS-3435", "VW", "T-Cross", 20000, 15),

                ("TUV-3637", "Fiat", "Mobi", 15000, 16),
                ("WXY-3839", "Chevrolet", "Spin", 85000, 17),
                ("ZAB-4041", "Toyota", "Yaris", 30000, 18),
                ("CDE-4243", "Honda", "Fit", 65000, 19),
                ("FGH-4445", "VW", "Voyage", 90000, 20),

                ("IJK-4647", "Renault", "Sandero", 70000, 21),
                ("LMN-4849", "Peugeot", "2008", 40000, 22),
                ("OPQ-5051", "Toyota", "Etios", 50000, 23),
                ("RST-5253", "Hyundai", "Azera", 85000, 24),
                ("UVW-5455", "Chevrolet", "S10", 120000, 25),
            ]

            for placa, marca, modelo, km, id_cliente in veiculos:
                upsert_veiculo(db, placa, marca, modelo, km, id_cliente)
            db.commit()

            # ORDENS DE SERVIÇO – 25 registros
            # Cada OS com 1 serviço, 1 peça e 1 pagamento
            agora = datetime.now()
            oses = []

            for i in range(1, 26):
                # Distribui status entre aberto, em execução e finalizado
                if i % 3 == 0:
                    status = StatusOS.finalizado
                elif i % 3 == 1:
                    status = StatusOS.em_execucao
                else:
                    status = StatusOS.aberto

                # Veículos e funcionários assumindo IDs de 1 a 25
                os_inst = OS(
                    id_veiculo=((i - 1) % 25) + 1,
                    id_responsavel=((i - 1) % 25) + 1,
                    km_entrada=80000 + i * 1500,
                    problema_relatado=f"Revisão periódica #{i}",
                    status=status,
                )
                db.add(os_inst)
                db.flush()  # garante que id_os é gerado
                oses.append(os_inst)

                # 1 serviço por OS, usando serviços de ID 1 a 4 em rodízio
                item_serv = ItemServico(
                    id_os=os_inst.id_os,
                    id_servico=((i - 1) % 4) + 1,  # assume que você tem pelo menos 4 serviços criados
                    qtd=1,
                    valor_unit=120.0 + (i % 3) * 30,  # valorzinho variando só pra não ficar tudo igual
                )
                db.add(item_serv)

                # 2-3 peças por OS, usando peças de ID 1 a 25 em rodízio
                num_pecas = 2 if i % 3 == 0 else 3  # alterna entre 2 e 3 peças
                for j in range(num_pecas):
                    item_peca = ItemPeca(
                        id_os=os_inst.id_os,
                        id_peca=((i - 1 + j) % 25) + 1,  # peças diferentes
                        qtd=1 if j == 0 else (j % 2) + 1,  # varia quantidade
                        valor_unit=60.0 + ((i + j) % 4) * 10,
                    )
                    db.add(item_peca)

                # Calcula total de peças
                db.flush()  # garante que as peças foram inseridas
                total_pecas = sum(float(p.qtd * p.valor_unit) for p in db.query(ItemPeca).filter_by(id_os=os_inst.id_os).all())
                
                # 1 pagamento por OS (simples)
                pagamento = Pagamento(
                    id_os=os_inst.id_os,
                    data=agora - timedelta(days=i),
                    forma="Dinheiro" if i % 2 == 0 else "Cartão",
                    valor=float(item_serv.valor_unit or 0) + total_pecas,
                )
                db.add(pagamento)

            db.commit()

            # AGENDAMENTOS – 25 registros
            agora = datetime.now()

            for i in range(1, 26):
                ag = Agendamento(
                    id_cliente=((i - 1) % 25) + 1,
                    id_veiculo=((i - 1) % 25) + 1,
                    id_servico=((i - 1) % 4) + 1,
                    data_hora=agora + timedelta(days=i, hours=(i % 5) * 2),
                    status=(
                        StatusAgendamento.pendente if i % 3 == 1 else
                        StatusAgendamento.confirmado if i % 3 == 2 else
                        StatusAgendamento.cancelado
                    )
                )
                db.add(ag)
            db.commit()

            # MOVIMENTOS
            tipos = ["entrada", "saida", "ajuste"]
            for i in range(1, 26):
                mov = MovimentoEstoque(
                    id_peca=((i - 1) % 25) + 1,
                    id_os=((i - 1) % 25) + 1,  # cada OS recebe um movimento
                    data=agora - timedelta(hours=i * 2),
                    tipo=tipos[i % 3],
                    origem="Fornecedor" if i % 2 == 0 else "Uso em manutenção",
                    qtd=(i % 3) + 1,
                    custo_unitario=40.0 + (i % 5) * 15,
                )
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
