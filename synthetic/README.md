# Synthetische dataset voor lokale ontwikkeling

Deze map bevat functies om een kleine, synthetische dataset te genereren en te laden die aansluit 
bij de queries die in dit project worden gebruikt. Zo kan je de Python-modules testen zonder 
dat je een applicatie-SQL-server (van Centric SSD) nodig hebt. Hiermee:

- Genereer je CSV's voor minimale bron-tabellen: `szclient`, `wvbesl`, `wvind_b`, `szregel`, `wvdos`, `abc_refcod`, `szukhis`, `szwerker`
- Laad je deze naar een ontwikkel-database in Docker (MSSQL / Postgres / MySQL / MariaDB / Oracle)


## CSV's genereren & laden in een ontwikkel‑DB

### 1) CSV's genereren

Ten eerste genereer je de synthetische CSV-bestanden. Voorbeeld:

```bash
python synthetic/generate_synthetic_data.py --out data/synthetic --rows 10 --seed 123
```

Dit schrijft synthetische data als `*.csv` naar `data/synthetic`.
    
### 2) CSV's laden in een ontwikkel‑DB (Docker)

Vervolgens laad je de synthetische CSV's in een ontwikkel-database in Docker. Hieronder een voorbeeld voor Postgres en Microsoft SQL Server.

Voorbeeld met Postgres:

```bash
python synthetic/load_csvs_to_db.py --db postgres --schema source --db-name source --csv-dir data/synthetic --force-refresh
```

Voorbeeld met Microsoft SQL Server:

```bash
python synthetic/load_csvs_to_db.py --db mssql --schema source --db-name source --csv-dir data/synthetic --force-refresh
```

Dit:
1) Start de SQL-server in Docker
2) Maakt database `source`/maakt schema `source`
3) Laadt elke CSV als tabel (bijv. `wvbesl.csv` -> `source.wvbesl`)

## Compleet voorbeeld (source → staging → silver)

Onderstaande commando voert het volledige proces uit met synthetische data:

```bash
PORT=55432 PASSWORD='SecureP@ss1!24323482349' ROWS=100 \
	chmod +x synthetic/examples/one_liner_postgres.sh && \
	./synthetic/examples/one_liner_postgres.sh
```

Let op dat je bovenstaande commando uitvoert in een bash-omgeving, zoals Git Bash. Zorg dat
hierin de Python-omgeving is geactiveerd (zie README.md in de hoofdmap), bijv., met `source venv/Scripts/activate`;
je moet ook eerst `uv sync` hebben gerund om de Python-dependencies te installeren. Daarnaast moet je
Docker dan wel Podman geïnstalleerd en actief hebben op je machine.

Het commando doet het volgende:
1) genereert synthetische CSV's;
2) start een Postgres‑container en laadt CSV's als tabellen in database `source` (schema: public);
3) maakt database `ggm` aan, waarin `staging` en `silver` als schema's worden gebruikt;
4) draait `sql_to_staging` om data te verplaatsen van database `source` → `ggm` (schema `staging`);
5) draait `staging_to_silver` om data te verplaatsen van `staging` -> `silver` (beide in database `ggm`).
Vooraf worden de doeltabellen naar het GGM-model in schema `silver` aangemaakt op basis van DDL's in `ggm_selectie/CSSD/`.

We gebruiken in dit voorbeeld dus één Postgres‑container (poort 55432) en twee databases (`source`, `ggm`).
In de praktijk zou `source` op één SQL-server staan (bijv. van de applicatie; Oracle DB) en `ggm` met `staging`/`silver` samen in een andere (datawarehouse,
bijv. Postgres of MSSQL).

> Tip: als je in VSCode werkt, kan je een extensie installeren zoals [PostgreSQL](https://marketplace.visualstudio.com/items?itemName=ckolkman.vscode-postgres);
hiermee kan je verbinding maken met de Docker‑container en de tabellen bekijken.
