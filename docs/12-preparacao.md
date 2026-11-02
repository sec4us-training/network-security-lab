# Preparação do laboratório

## Dimensionamento

| VM | vCPU | RAM | Disco |
|---|---:|---:|---:|
| FW01 | 2 | 2 GB | 20 GB |
| APP01 | 1 | 1 GB | 10 GB |
| DB01 | 1 | 1 GB | 10 GB |
| WEB01 | 1 | 1 GB | 10 GB |
| EXT01 | 1 | 1 GB | 10 GB |
| **Total** | **6** | **6 GB** | **60 GB** |

## Redes virtuais

- `WAN-NET`: EXT01 + FW01 eth0
- `LAN-NET`: APP01 + DB01 + FW01 eth1
- `DMZ-NET`: WEB01 + FW01 eth2

Evite conectar as redes didáticas diretamente à rede física. Use Debian ou Ubuntu Server em todas as VMs. Instale `iptables`, `conntrack`, `tcpdump`, `curl`, `netcat`, `traceroute`, `squid` e os serviços específicos de cada servidor.

## Fluxo recomendado

1. Crie snapshots iniciais.
2. Configure IPs estáticos e gateways.
3. Ative o IP forwarding no FW01.
4. Comece pela fase de roteamento puro.
5. Restaure snapshots ou limpe regras e conexões entre fases.
6. Use `iptables-save` e `iptables-restore` para demonstrar persistência.

**Nota:** distribuições modernas podem usar o backend iptables-nft. Registre a versão (`iptables -V`) para manter os exercícios reproduzíveis.
