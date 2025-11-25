# 🔧 EP_BD_Mecanica

Trabalho para a disciplina de Banco de Dados I 2025

Sistema web completo de gerenciamento de oficina mecânica com cadastro de clientes, veículos, serviços, peças e geração de relatórios de manutenção.

---

## 🎯 Funcionalidades Principais

✅ **3.1 - Listar Peças Danificadas**
- Consultar peças que precisam de troca por veículo
- Exibir complexidade (nacional ou importada)

✅ **3.2 - Agendar Serviços**
- Clientes agendarem serviços com data, horário e tipo escolhidos
- Validação de conflitos de horário

✅ **3.3 - Relatórios de Manutenção**
- Histórico completo de serviços realizados
- Detalhamento de peças usadas e pagamentos
- Acompanhamento e futuras consultas

---

## 🚀 Quick Start

### **1. Pré-requisitos**
- Docker e Docker Compose instalados
- Git (opcional)

### **2. Clonar/Extrair Projeto**
```bash
git clone https://github.com/RidenLilith/EP_BD_Mecanica.git
cd EP_BD_Mecanica
```

### **3. Iniciar Serviços**
```bash
docker-compose up -d
```

### **4. Popular Banco de Dados**
```bash
docker-compose exec -T backend python seed.py
```

### **5. Acessar Sistema**
Abra no navegador: **http://localhost:8081**

---

## 📖 Setup Detalhado

Veja o arquivo [`SETUP.md`](./SETUP.md) para instruções completas de configuração e uso.

---

## 📂 Arquitetura do Projeto

```
├── back-end/           # API Flask + SQLAlchemy
│   ├── app.py         # Endpoints REST
│   ├── models.py      # Modelos do banco
│   ├── database.py    # Configuração PostgreSQL
│   └── seed.py        # Dados de teste
├── frontend/          # Interface web
│   ├── index.html     # Interface principal
│   ├── js/api.js      # Chamadas para API
│   └── css/style.css  # Estilos
└── docker-compose.yml # Orquestração
```

---

## 🛠️ Stack Tecnológico

| Camada | Tecnologia |
|--------|-----------|
| **Frontend** | HTML5, CSS3, JavaScript, Bootstrap 5 |
| **Backend** | Python, Flask, Flask-CORS |
| **Banco** | PostgreSQL 16 |
| **ORM** | SQLAlchemy |
| **DevOps** | Docker, Docker Compose |
| **Servidor** | Nginx |

---

## 📊 Dados Inclusos

O script `seed.py` popula:
- 10 clientes
- 12 veículos
- 15 serviços
- 25 peças
- 8 funcionários
- 8 fornecedores
- 10 ordens de serviço
- 12 agendamentos
- 15 movimentos de estoque

---

## 🎓 Requisitos Atendidos

- ✅ Modelagem de banco de dados em ER
- ✅ Implementação em PostgreSQL
- ✅ Interface web funcional (CRUD)
- ✅ 3 funcionalidades específicas (3.1, 3.2, 3.3)
- ✅ Dados de teste para validação
- ✅ Documentação completa

---

## 📞 URLs Importantes

| Serviço | URL |
|---------|-----|
| **Frontend** | http://localhost:8081 |
| **Backend API** | http://localhost:5000/api |
| **Adminer (BD)** | http://localhost:8080 |
| **GitHub** | https://github.com/RidenLilith/EP_BD_Mecanica |

---

## 🆘 Problemas?

Veja a seção "Troubleshooting" em [`SETUP.md`](./SETUP.md)

---

**Desenvolvido para Banco de Dados I - 2025** 🚗✨
