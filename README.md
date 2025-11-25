README — EP_BD_Mecanica (versão curta, direta e sem paciência)

Clone o repositório, entre na pasta e rode esses comandos. Só isso.

1) Criar venv e instalar dependências
PowerShell:
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r back-end/requirements.txt

Linux/macOS:
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r back-end/requirements.txt

2) (Opcional) Definir DATABASE_URL
Se quiser usar Postgres. Se não definir nada, vira sqlite e funciona igual.

PowerShell:
$env:DATABASE_URL = "postgresql://app:app@localhost:5432/ep_bd"

Linux/macOS:
export DATABASE_URL="postgresql://app:app@localhost:5432/ep_bd"

3) Rodar o sistema
python run_local.py

O script roda o seed, levanta o backend e serve o frontend.
Ele abre sozinho no navegador. Se não abrir, vá para o endereço que ele imprimir (normalmente http://localhost:8081).
Copie o erro do terminal e pronto. Não tem mágica.
