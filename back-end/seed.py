from database import SessionLocal, engine, Base
from models import Cliente, Veiculo, Funcionario, Servico, Peca, OrigemPeca

print("🔄 Criando sessão...")
db = SessionLocal()

def reset_tables():
    print("🧨 Limpando tabelas...")
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

def seed():
    print("🌱 Inserindo dados iniciais...")

    # Clientes
    c1 = Cliente(nome_razao="João da Silva", cpf_cnpj="123.456.789-00")
    c2 = Cliente(nome_razao="Maria Oliveira", cpf_cnpj="987.654.321-00")
    c3 = Cliente(nome_razao="Auto Peças Avenida LTDA", cpf_cnpj="12.345.678/0001-99")

    db.add_all([c1, c2, c3])
    db.commit()

    # IMPORTANTE: refresh para pegar IDs
    db.refresh(c1); db.refresh(c2); db.refresh(c3)

    # VEÍCULOS → Aqui vou preencher quando você escolher o estilo
    # Exemplo genérico (será substituído):
    v1 = Veiculo(placa="ABC1A23", modelo="Modelo X", marca="Marca X", id_cliente=c1.id_cliente)
    v2 = Veiculo(placa="DEF4B56", modelo="Modelo Y", marca="Marca Y", id_cliente=c2.id_cliente)
    db.add_all([v1, v2])

    # Funcionários
    f1 = Funcionario(nome="Carlos Mecânico", funcao="Mecânico Geral")
    f2 = Funcionario(nome="Ana Recepção", funcao="Atendimento")
    db.add_all([f1, f2])

    # Serviços (exemplos genéricos — vou trocar conforme estilo)
    s1 = Servico(descricao="Troca de óleo", preco_padrao=120)
    s2 = Servico(descricao="Revisão básica", preco_padrao=350)
    db.add_all([s1, s2])

    # Peças
    p1 = Peca(sku="FILTRO-001", descricao="Filtro de óleo", origem=OrigemPeca.nacional, estoque_atual=25)
    p2 = Peca(sku="PASTILHA-002", descricao="Pastilha de freio", origem=OrigemPeca.importada, estoque_atual=10)
    db.add_all([p1, p2])

    db.commit()
    print("✅ Seed inserido com sucesso!")

if __name__ == "__main__":
    reset_tables()
    seed()
