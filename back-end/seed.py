from sqlalchemy.dialects.postgresql import insert
from sqlalchemy import text
from database import SessionLocal, Base, engine
from models import Cliente, Servico, Peca, Funcionario  # Fornecedor só se usar

print("🔄 Criando sessão...")
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
    # se não tiver UNIQUE em (nome), tudo bem: será sempre insert
    stmt = insert(Funcionario.__table__).values(nome=nome, funcao=funcao)
    db.execute(stmt)

# (Opcional) reset total de schema:
def reset_tables():
    print("🧨 Dropando e recriando schema...")
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

# ---------- SEED ----------
def seed():
    print("🌱 Inserindo dados iniciais (idempotente)...")

    upsert_cliente("João da Silva", "123.456.789-00")
    upsert_cliente("Oficina XPTO Ltda", "12.345.678/0001-99")

    upsert_servico("Troca de óleo", 120.00)
    upsert_servico("Alinhamento", 150.00)

    upsert_peca("OL-10W40", "Óleo 10W40", "nacional", 20)
    upsert_peca("FILT-AR-FOX", "Filtro de ar FOX", "importada", 5)

    upsert_funcionario("Pedro Mecânico", "Mecânico")
    upsert_funcionario("Ana Recepção", "Atendimento")

    db.commit()
    print("✅ Seed inserido com sucesso!")

if __name__ == "__main__":
    reset_tables()
    seed()
