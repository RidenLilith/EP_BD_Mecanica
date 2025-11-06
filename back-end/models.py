# backend/models.py
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Numeric, Enum, Text
from sqlalchemy.orm import relationship
from database import Base
import enum

# --- Auxiliares ---
class OrigemPeca(str, enum.Enum):
    nacional = "nacional"
    importada = "importada"

class StatusAgendamento(str, enum.Enum):
    pendente = "pendente"
    confirmado = "confirmado"
    concluido = "concluido"
    cancelado = "cancelado"

class StatusOS(str, enum.Enum):
    aberto = "aberto"
    em_andamento = "em_andamento"
    fechado = "fechado"
    cancelado = "cancelado"

# --- Núcleo do domínio ---
class Cliente(Base):
    __tablename__ = "cliente"
    id_cliente = Column(Integer, primary_key=True)
    nome_razao = Column(String(120), nullable=False)
    cpf_cnpj = Column(String(20), nullable=True, unique=True)

    veiculos = relationship("Veiculo", back_populates="cliente")

class Veiculo(Base):
    __tablename__ = "veiculo"
    id_veiculo = Column(Integer, primary_key=True)
    placa = Column(String(10), nullable=False, unique=True)
    chassi = Column(String(32), nullable=True)
    km_atual = Column(Integer, nullable=True)
    marca = Column(String(60), nullable=True)
    modelo = Column(String(60), nullable=True)

    id_cliente = Column(Integer, ForeignKey("cliente.id_cliente"), nullable=False)
    cliente = relationship("Cliente", back_populates="veiculos")

    ordens = relationship("OS", back_populates="veiculo")

class Funcionario(Base):
    __tablename__ = "funcionario"
    id_funcionario = Column(Integer, primary_key=True)
    nome = Column(String(120), nullable=False)
    funcao = Column(String(80), nullable=True)

    ordens = relationship("OS", back_populates="responsavel")

class Servico(Base):
    __tablename__ = "servico"
    id_servico = Column(Integer, primary_key=True)
    descricao = Column(String(160), nullable=False)
    preco_padrao = Column(Numeric(10,2), nullable=True)

class Peca(Base):
    __tablename__ = "peca"
    id_peca = Column(Integer, primary_key=True)
    sku = Column(String(60), nullable=False, unique=True)
    descricao = Column(String(160), nullable=False)
    origem = Column(Enum(OrigemPeca), nullable=False, default=OrigemPeca.nacional)
    estoque_atual = Column(Integer, nullable=False, default=0)

class OS(Base):  # Ordem de Serviço
    __tablename__ = "os"
    id_os = Column(Integer, primary_key=True)
    status = Column(Enum(StatusOS), nullable=False, default=StatusOS.aberto)
    problema_relatado = Column(Text, nullable=True)
    km_entrada = Column(Integer, nullable=True)

    id_veiculo = Column(Integer, ForeignKey("veiculo.id_veiculo"), nullable=False)
    id_funcionario = Column(Integer, ForeignKey("funcionario.id_funcionario"), nullable=False)

    veiculo = relationship("Veiculo", back_populates="ordens")
    responsavel = relationship("Funcionario", back_populates="ordens")

    itens_servico = relationship("ItemServico", back_populates="os", cascade="all, delete-orphan")
    itens_peca = relationship("ItemPeca", back_populates="os", cascade="all, delete-orphan")
    pagamentos = relationship("Pagamento", back_populates="os", cascade="all, delete-orphan")

class ItemServico(Base):
    __tablename__ = "item_servico"
    id_item_servico = Column(Integer, primary_key=True)
    qtd = Column(Integer, nullable=False, default=1)
    valor_unit = Column(Numeric(10,2), nullable=True)

    id_os = Column(Integer, ForeignKey("os.id_os"), nullable=False)
    id_servico = Column(Integer, ForeignKey("servico.id_servico"), nullable=False)

    os = relationship("OS", back_populates="itens_servico")
    servico = relationship("Servico")

class ItemPeca(Base):
    __tablename__ = "item_peca"
    id_item_peca = Column(Integer, primary_key=True)
    qtd = Column(Integer, nullable=False, default=1)
    valor_unit = Column(Numeric(10,2), nullable=True)
    # Para 3.1, consideramos que toda peça lançada aqui é "danificada/para troca" na OS.
    # Se quiser, adicione um status_peca_troca boolean ou enum.

    id_os = Column(Integer, ForeignKey("os.id_os"), nullable=False)
    id_peca = Column(Integer, ForeignKey("peca.id_peca"), nullable=False)

    os = relationship("OS", back_populates="itens_peca")
    peca = relationship("Peca")

class Pagamento(Base):
    __tablename__ = "pagamento"
    id_pagamento = Column(Integer, primary_key=True)
    data = Column(DateTime, nullable=False)
    forma = Column(String(30), nullable=False)
    valor = Column(Numeric(10,2), nullable=False)

    id_os = Column(Integer, ForeignKey("os.id_os"), nullable=False)
    os = relationship("OS", back_populates="pagamentos")

class Agendamento(Base):
    __tablename__ = "agendamento"
    id_agendamento = Column(Integer, primary_key=True)
    data_hora = Column(DateTime, nullable=False)
    status = Column(Enum(StatusAgendamento), nullable=False, default=StatusAgendamento.pendente)

    id_cliente = Column(Integer, ForeignKey("cliente.id_cliente"), nullable=False)
    id_veiculo = Column(Integer, ForeignKey("veiculo.id_veiculo"), nullable=False)
    id_servico = Column(Integer, ForeignKey("servico.id_servico"), nullable=False)

    cliente = relationship("Cliente")
    veiculo = relationship("Veiculo")
    servico = relationship("Servico")
