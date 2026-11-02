# Aplicação de exemplo (Django + PostgreSQL)

Projeto web usado pelo laboratório. A **mesma base de código** roda em:

- **APP01** (`10.10.10.10`) — aplicação interna na LAN.
- **WEB01** (`172.16.20.10`) — web pública na DMZ, atrás do Nginx.

Ambas conectam ao **PostgreSQL do DB01** (`10.10.10.20:5432`). Toda a configuração
vem de variáveis de ambiente (ver [.env.example](.env.example)).

## Dados de exemplo

O seed é feito por uma **data migration** ([core/migrations/0002_seed_data.py](core/migrations/0002_seed_data.py)),
então o **primeiro `migrate` já popula o banco** com os hosts e eventos do lab.
Não é preciso rodar nenhum comando extra de carga.

## Subir localmente (para testar a aplicação)

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env            # ajuste DB_HOST etc.
set -a && . ./.env && set +a    # exporta as variáveis do .env
python manage.py migrate        # cria o schema e popula os dados
python manage.py createsuperuser  # opcional, para /admin
python manage.py runserver 0.0.0.0:8000
```

A instalação completa por máquina (gunicorn, systemd, Nginx) está em
[../docs/12-preparacao.md](../docs/12-preparacao.md).

## Rotas

- `/` — página com hosts e eventos lidos do PostgreSQL.
- `/admin/` — administração do Django.
- `/healthz` — verificação de saúde (inclui conectividade com o banco).
