# Preparação do laboratório

[← Índice](../README.md)

> **Escopo desta fase:** instalar e configurar as ferramentas/serviços de cada
> máquina com a VM **online, com acesso normal à Internet** (para baixar pacotes
> via `apt`/`pip`/`git`). A segmentação em redes isoladas, o roteamento, o NAT e
> as regras de firewall são tratados nas fases seguintes. Faça esta instalação
> **antes** de aplicar o isolamento de rede do laboratório.

## Dimensionamento

| VM | vCPU | RAM | Disco |
|---|---:|---:|---:|
| FW01 | 2 | 2 GB | 20 GB |
| APP01 | 1 | 1 GB | 10 GB |
| DB01 | 1 | 1 GB | 10 GB |
| WEB01 | 1 | 1 GB | 10 GB |
| EXT01 | 1 | 1 GB | 10 GB |
| **Total** | **6** | **6 GB** | **60 GB** |

## Redes virtuais (configurar depois)

- `WAN-NET`: EXT01 + FW01 eth0
- `LAN-NET`: APP01 + DB01 + FW01 eth1
- `DMZ-NET`: WEB01 + FW01 eth2

Evite conectar as redes didáticas diretamente à rede física. Use Debian 12 ou
Ubuntu Server 22.04/24.04 em todas as VMs. Durante a instalação dos pacotes,
mantenha a VM com uma interface NAT/bridge com Internet; você pode removê-la ao
montar a topologia isolada.

## Resumo de ferramentas por máquina

| Máquina | Papel | Principais pacotes/serviços |
|---|---|---|
| EXT01 | Cliente WAN + site externo simulado | `curl`, `nmap`, `netcat`, `tcpdump` + **Nginx** (página estática) |
| FW01 | Firewall e proxy | `iptables`/`nftables`, `iptables-persistent`, `conntrack`, `tcpdump`, **Squid** |
| APP01 | Aplicação web interna | **Python/Django + Gunicorn** (conecta no PostgreSQL do DB01) |
| DB01 | Banco de dados e DNS | **PostgreSQL**, `bind9` |
| WEB01 | Web pública (DMZ) | **Python/Django + Gunicorn + Nginx** (conecta no PostgreSQL do DB01) |

---

## 0. Base comum a todas as VMs

Execute em **todas** as máquinas:

```bash
sudo apt update && sudo apt -y full-upgrade

sudo apt -y install \
  vim curl wget ca-certificates gnupg git htop \
  iproute2 net-tools tcpdump traceroute mtr-tiny dnsutils \
  netcat-openbsd nmap openssh-server

# SSH ligado (acesso administrativo nas próximas fases)
sudo systemctl enable --now ssh

# Registre a versão do iptables para reprodutibilidade (nft x legacy)
iptables -V
```

As máquinas que usam o projeto Django (APP01 e WEB01) e o DB01 compartilham o
mesmo repositório. Clone-o onde for necessário (ajuste a URL do seu remoto):

```bash
sudo git clone https://github.com/SEU-USUARIO/network-security-lab.git /opt/network-security-lab
```

---

## 1. EXT01 — cliente externo + site simulado

Ferramentas de teste já vieram na base (`curl`, `nmap`, `netcat`, `tcpdump`,
`traceroute`). Falta publicar a página estática que simula um site na Internet
(alvo dos testes de saída via Squid).

```bash
sudo apt -y install nginx

# Publica a página de exemplo do repositório
sudo mkdir -p /var/www/ext01
sudo cp /opt/network-security-lab/sites/ext01/index.html /var/www/ext01/

# Server block dedicado
sudo tee /etc/nginx/sites-available/ext01 >/dev/null <<'NGINX'
server {
    listen 80 default_server;
    server_name _;
    root /var/www/ext01;
    index index.html;
    location / { try_files $uri $uri/ =404; }
}
NGINX

sudo rm -f /etc/nginx/sites-enabled/default
sudo ln -sf /etc/nginx/sites-available/ext01 /etc/nginx/sites-enabled/ext01
sudo nginx -t && sudo systemctl enable --now nginx

# Verificação
curl -s http://localhost/ | head
```

---

## 2. FW01 — firewall e proxy

Apenas **instalação** das ferramentas. As regras de roteamento, NAT e as ACLs do
Squid são aplicadas nas fases 01, 04–06 e 09.

```bash
sudo apt -y install iptables iptables-persistent nftables conntrack tcpdump squid
```

> Durante a instalação, o `iptables-persistent` pergunta se deseja salvar as
> regras atuais (IPv4/IPv6). Pode aceitar — nesta fase ainda não há regras.

```bash
# Backup da configuração original do Squid antes de editar nas próximas fases
sudo cp /etc/squid/squid.conf /etc/squid/squid.conf.orig
sudo systemctl enable squid

# Conferências
iptables -V
conntrack -L 2>/dev/null; echo "conntrack OK"
squid -v | head -1
```

> O `net.ipv4.ip_forward`, as regras `FORWARD`/`nat` e as ACLs do Squid serão
> configurados nas fases de roteamento, NAT e proxy — não agora.

---

## 3. DB01 — PostgreSQL e DNS

### 3.1 PostgreSQL

```bash
sudo apt -y install postgresql postgresql-contrib

# Cria o usuário e o banco usados pela aplicação
sudo -u postgres psql -c "CREATE USER labuser WITH PASSWORD 'labpass';"
sudo -u postgres psql -c "CREATE DATABASE labdb OWNER labuser;"
```

Permitir conexões da LAN (APP01) e da DMZ (WEB01 → DB01:5432):

```bash
PG_VER=$(ls /etc/postgresql | sort -n | tail -1)
PG_DIR="/etc/postgresql/$PG_VER/main"

# Escuta em todas as interfaces
sudo sed -i "s/^#\?listen_addresses.*/listen_addresses = '*'/" "$PG_DIR/postgresql.conf"

# Autenticação para LAN e DMZ
echo "host    labdb   labuser   10.10.10.0/24    scram-sha-256"  | sudo tee -a "$PG_DIR/pg_hba.conf"
echo "host    labdb   labuser   172.16.20.0/24   scram-sha-256"  | sudo tee -a "$PG_DIR/pg_hba.conf"

sudo systemctl restart postgresql
sudo systemctl enable postgresql

# Verificação local
sudo -u postgres psql -c "\l" | grep labdb
```

> Na fase isolada, a liberação em `pg_hba.conf` é o controle de acesso do banco;
> o firewall (FW01) e o firewall de host complementam essa política.

### 3.2 DNS (bind9) — opcional

```bash
sudo apt -y install bind9 bind9-utils
sudo systemctl enable --now named
```

A configuração das zonas do laboratório é feita no exercício de DNS. Por ora o
serviço fica instalado e ativo com a configuração padrão (resolvedor).

---

## 4. APP01 — aplicação web interna (Django)

> O `migrate` precisa alcançar o PostgreSQL do DB01 (`10.10.10.20:5432`).
> Garanta que o DB01 já está instalado e acessível quando executar este passo.

```bash
sudo apt -y install python3 python3-venv python3-pip git

cd /opt/network-security-lab/app
python3 -m venv .venv
.venv/bin/pip install --upgrade pip
.venv/bin/pip install -r requirements.txt

# Configuração da instância (papel APP01)
cp .env.example .env
sed -i 's/^APP_ROLE=.*/APP_ROLE=APP01/' .env
# DB_HOST já aponta para 10.10.10.20 no .env.example; ajuste se necessário.

# Carrega o .env e aplica as migrações (cria o schema E popula os dados de exemplo)
set -a && . ./.env && set +a
.venv/bin/python manage.py migrate
.venv/bin/python manage.py collectstatic --noinput
.venv/bin/python manage.py createsuperuser   # opcional, para o /admin
```

Serviço Gunicorn (porta 80) via systemd:

```bash
sudo tee /etc/systemd/system/labapp.service >/dev/null <<'UNIT'
[Unit]
Description=Lab Django app (APP01)
After=network.target

[Service]
WorkingDirectory=/opt/network-security-lab/app
EnvironmentFile=/opt/network-security-lab/app/.env
ExecStart=/opt/network-security-lab/app/.venv/bin/gunicorn labsite.wsgi:application --bind 0.0.0.0:80 --workers 2
Restart=on-failure

[Install]
WantedBy=multi-user.target
UNIT

sudo systemctl daemon-reload
sudo systemctl enable --now labapp

# Verificação
curl -s http://localhost/healthz; echo
curl -s http://localhost/ | grep -i APP01
```

---

## 5. WEB01 — web pública na DMZ (Django + Nginx)

Usa o mesmo projeto, com papel `WEB01`, atrás do Nginx. O Gunicorn escuta apenas
em `127.0.0.1:8000` e o Nginx publica na porta 80 (depois exposta via DNAT em
FW01:8080).

```bash
sudo apt -y install python3 python3-venv python3-pip git nginx

cd /opt/network-security-lab/app
python3 -m venv .venv
.venv/bin/pip install --upgrade pip
.venv/bin/pip install -r requirements.txt

# Configuração da instância (papel WEB01)
cp .env.example .env
sed -i 's/^APP_ROLE=.*/APP_ROLE=WEB01/' .env
# Confirme no .env: DB_HOST=10.10.10.20 e DJANGO_CSRF_TRUSTED_ORIGINS
# incluindo http://203.0.113.1:8080 (publicação via DNAT) e http://172.16.20.10

set -a && . ./.env && set +a
.venv/bin/python manage.py migrate       # idempotente: o seed usa get_or_create
.venv/bin/python manage.py collectstatic --noinput
```

Gunicorn (loopback) via systemd:

```bash
sudo tee /etc/systemd/system/labweb.service >/dev/null <<'UNIT'
[Unit]
Description=Lab Django app (WEB01)
After=network.target

[Service]
WorkingDirectory=/opt/network-security-lab/app
EnvironmentFile=/opt/network-security-lab/app/.env
ExecStart=/opt/network-security-lab/app/.venv/bin/gunicorn labsite.wsgi:application --bind 127.0.0.1:8000 --workers 2
Restart=on-failure

[Install]
WantedBy=multi-user.target
UNIT

sudo systemctl daemon-reload
sudo systemctl enable --now labweb
```

Nginx como proxy reverso (porta 80) e servindo os estáticos:

```bash
sudo tee /etc/nginx/sites-available/labweb >/dev/null <<'NGINX'
server {
    listen 80 default_server;
    server_name _;

    location /static/ {
        alias /opt/network-security-lab/app/staticfiles/;
    }

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
NGINX

sudo rm -f /etc/nginx/sites-enabled/default
sudo ln -sf /etc/nginx/sites-available/labweb /etc/nginx/sites-enabled/labweb
sudo nginx -t && sudo systemctl enable --now nginx

# Verificação
curl -s http://localhost/healthz; echo
curl -s http://localhost/ | grep -i WEB01
```

---

## Fluxo recomendado (após a instalação)

1. Crie snapshots iniciais de cada VM já com as ferramentas instaladas.
2. Monte as redes virtuais isoladas e configure IPs estáticos e gateways.
3. Ative o IP forwarding no FW01.
4. Comece pela fase de roteamento puro.
5. Restaure snapshots ou limpe regras e conexões entre fases.
6. Use `iptables-save` e `iptables-restore` para demonstrar persistência.

**Nota:** distribuições modernas podem usar o backend iptables-nft. Registre a
versão (`iptables -V`) para manter os exercícios reproduzíveis.

---

© 2026 Sec4US. Todos os direitos reservados. Conteúdo do treinamento 'Introdução a Redes IPv4'. É proibido o compartilhamento, a divulgação ou a reprodução deste material sem aprovação prévia por escrito da Sec4US.
