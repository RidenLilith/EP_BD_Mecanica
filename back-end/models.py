import enum
from datetime import datetime
from sqlalchemy import (
    Column, Integer, String, ForeignKey, DateTime, Numeric,
    Enum, Table
)
from sqlalchemy.orm import relationship
from database import Base
from sqlalchemy.sql import func


# ======================================================
# ENUMS
# ======================================================

class OrigemPeca(str, enum.Enum):
    nacional = "nacional"
    importada = "importada"

class StatusAgendamento(str, enum.Enum):
    pendente = "pendente"
    confirmado = "confirmado"
    cancelado = "cancelado"

class StatusOS(str, enum.Enum):
    aberto = "aberto"
    em_execucao = "em_execucao"
    finalizado = "finalizado"
    cancelado = "cancelado"

class TipoMovimento(str, enum.Enum):
    entrada = "entrada"
    saida = "saida"
    ajuste = "ajuste"

# ======================================================
# CLIENTE
# ======================================================

class Cliente(Base):
    __tablename__ = "cliente"

    id_cliente = Column(Integer, primary_key=True)
    nome_razao = Column(String(120), nullable=False)
    cpf_cnpj = Column(String(20), nullable=False, unique=True, index=True)

    veiculos = relationship("Veiculo", back_populates="cliente")

# ======================================================
# VEÍCULO
# ======================================================

class Veiculo(Base):
    __tablename__ = "veiculo"

    id_veiculo = Column(Integer, primary_key=True)
    placa = Column(String(10), nullable=False, unique=True)
    chassi = Column(String(50))
    km_atual = Column(Integer)
    marca = Column(String(50))
    modelo = Column(String(50))

    id_cliente = Column(Integer, ForeignKey("cliente.id_cliente"), nullable=False)
    cliente = relationship("Cliente", back_populates="veiculos")

    ordens = relationship("OS", back_populates="veiculo")

# ======================================================
# FUNCIONÁRIO
# ======================================================

class Funcionario(Base):
    __tablename__ = "funcionario"

    id_funcionario = Column(Integer, primary_key=True)
    nome = Column(String(120), nullable=False)
    funcao = Column(String(120))

    ordens = relationship("OS", back_populates="responsavel")

# ======================================================
# SERVIÇO
# ======================================================

class Servico(Base):
    __tablename__ = "servico"

    id_servico = Column(Integer, primary_key=True)
    descricao = Column(String(200), nullable=False, unique=True, index=True)
    preco_padrao = Column(Numeric(10, 2))

    itens_servico = relationship("ItemServico", back_populates="servico")

# ======================================================
# PEÇA
# ======================================================

class Peca(Base):
    __tablename__ = "peca"

    id_peca = Column(Integer, primary_key=True)
    sku = Column(String(50), nullable=False, unique=True, index=True)
    descricao = Column(String(200), nullable=False)
    origem = Column(Enum(OrigemPeca), nullable=False, default=OrigemPeca.nacional)
    estoque_atual = Column(Integer, nullable=False, default=0)

    itens_peca = relationship("ItemPeca", back_populates="peca")
    movimentos = relationship("MovimentoEstoque", back_populates="peca")
    fornecedores = relationship("Fornecedor", secondary="fornecedor_peca", back_populates="pecas")

# ======================================================
# FORNECEDOR (N:N com peça)
# ======================================================

class Fornecedor(Base):
    __tablename__ = "fornecedor"

    id_fornecedor = Column(Integer, primary_key=True)
    nome_razao = Column(String(120), nullable=False)
    cpf_cnpj = Column(String(20), unique=True)

    pecas = relationship("Peca", secondary="fornecedor_peca", back_populates="fornecedores")

fornecedor_peca = Table(
    "fornecedor_peca", Base.metadata,
    Column("id_fornecedor", Integer, ForeignKey("fornecedor.id_fornecedor"), primary_key=True),
    Column("id_peca", Integer, ForeignKey("peca.id_peca"), primary_key=True),
)

# ======================================================
# ORDEM DE SERVIÇO
# ======================================================

class OS(Base):
    __tablename__ = "os"

    id_os = Column(Integer, primary_key=True)
    status = Column(Enum(StatusOS), nullable=False, default=StatusOS.aberto)
    problema_relatado = Column(String(255))
    km_entrada = Column(Integer)

    id_veiculo = Column(Integer, ForeignKey("veiculo.id_veiculo"), nullable=False)
    veiculo = relationship("Veiculo", back_populates="ordens")

    id_responsavel = Column(Integer, ForeignKey("funcionario.id_funcionario"), nullable=False)
    responsavel = relationship("Funcionario", back_populates="ordens")

    itens_servico = relationship("ItemServico", back_populates="os")
    itens_peca = relationship("ItemPeca", back_populates="os")
    pagamentos = relationship("Pagamento", back_populates="os")
    movimentos = relationship("MovimentoEstoque", back_populates="os")

# ======================================================
# ITEM SERVIÇO (N : N entre OS e Serviço)
# ======================================================

class ItemServico(Base):
    __tablename__ = "item_servico"

    id_item_servico = Column(Integer, primary_key=True)
    qtd = Column(Integer, nullable=False, default=1)
    valor_unit = Column(Numeric(10,2))

    id_os = Column(Integer, ForeignKey("os.id_os"), nullable=False)
    os = relationship("OS", back_populates="itens_servico")

    id_servico = Column(Integer, ForeignKey("servico.id_servico"), nullable=False)
    servico = relationship("Servico", back_populates="itens_servico")

# ======================================================
# ITEM PEÇA (N : N entre OS e Peça)
# ======================================================

class ItemPeca(Base):
    __tablename__ = "item_peca"

    id_item_peca = Column(Integer, primary_key=True)
    qtd = Column(Integer, nullable=False, default=1)
    valor_unit = Column(Numeric(10,2))

    id_os = Column(Integer, ForeignKey("os.id_os"), nullable=False)
    os = relationship("OS", back_populates="itens_peca")

    id_peca = Column(Integer, ForeignKey("peca.id_peca"), nullable=False)
    peca = relationship("Peca", back_populates="itens_peca")

# ======================================================
# PAGAMENTO
# ======================================================

class Pagamento(Base):
    __tablename__ = "pagamento"

    id_pagamento = Column(Integer, primary_key=True)
    data = Column(DateTime, default=func.now())
    forma = Column(String(50))
    valor = Column(Numeric(10,2))

    id_os = Column(Integer, ForeignKey("os.id_os"), nullable=False)
    os = relationship("OS", back_populates="pagamentos")

# ======================================================
# MOVIMENTO ESTOQUE (1:N peça, opcionalmente OS)
# ======================================================

class MovimentoEstoque(Base):
    __tablename__ = "movimento_estoque"

    id_movimento = Column(Integer, primary_key=True)
    data = Column(DateTime, nullable=False, default=func.now())
    tipo = Column(Enum(TipoMovimento), nullable=False)
    origem = Column(String(80))
    qtd = Column(Integer, nullable=False)
    custo_unitario = Column(Numeric(10,2))

    id_os = Column(Integer, ForeignKey("os.id_os"))
    os = relationship("OS", back_populates="movimentos")

    id_peca = Column(Integer, ForeignKey("peca.id_peca"), nullable=False)
    peca = relationship("Peca", back_populates="movimentos")

# ======================================================
# AGENDAMENTO
# ======================================================

class Agendamento(Base):
    __tablename__ = "agendamento"

    id_agendamento = Column(Integer, primary_key=True)
    data_hora = Column(DateTime, nullable=False)
    status = Column(Enum(StatusAgendamento), nullable=False, default=StatusAgendamento.pendente)

    id_cliente = Column(Integer, ForeignKey("cliente.id_cliente"), nullable=False)
    cliente = relationship("Cliente")

    id_veiculo = Column(Integer, ForeignKey("veiculo.id_veiculo"), nullable=False)
    veiculo = relationship("Veiculo")

    id_servico = Column(Integer, ForeignKey("servico.id_servico"), nullable=False)
    servico = relationship("Servico")
