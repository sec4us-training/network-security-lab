# Matriz de comunicação — objetivo final

| Origem | Destino | Serviço | Política |
|---|---|---|---|
| WAN | DMZ | HTTP/HTTPS via DNAT | Permitir |
| WAN | LAN | Qualquer | Bloquear |
| LAN | WAN | HTTP via Squid | Permitir |
| LAN | WAN | HTTP direto | Bloquear |
| LAN | DMZ | SSH administrativo | Permitir seletivamente |
| DMZ (WEB01) | DB01 | TCP/5432 | Permitir |
| DMZ | APP01 | Qualquer | Bloquear |
| DMZ | WAN | Serviços autorizados | Permitir seletivamente |
| APP01 | DB01 | LAN local | Permitir (não passa por FW01) |

**Atenção:** as políticas de aplicação e do firewall de host também devem ser consideradas. A comunicação lateral na mesma subnet não é filtrada pelo FW01.
