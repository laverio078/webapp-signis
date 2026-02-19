# 🛡️ SIGNIS WebApp - Interfaccia di Gestione NIS2

![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-000000?style=for-the-badge&logo=flask&logoColor=white)
![Bootstrap](https://img.shields.io/badge/Bootstrap_5-7952B3?style=for-the-badge&logo=bootstrap&logoColor=white)
![Tests](https://img.shields.io/badge/Unit_Tests-19%2F19_Passed-brightgreen?style=for-the-badge)
![Status](https://img.shields.io/badge/Project-Bonus_Track-FFDD00?style=for-the-badge)
![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)

Questa cartella contiene l'interfaccia web del progetto SIGNIS, è una demo app che magari potrebbe essere utile a qualcuno come base di sviluppo. Non ha uno stile accademico perchè per me è una bonus track e per quanto abbia rispetto per lo stile, qui uso il mio da neurodivergente.

Visto che gestire un database relazionale interamente da riga di comando (o tramite pgAdmin) non è proprio "user-friendly" per chi deve compilare i registri NIS2 in azienda, ho speso 50 centesimi del mio tempo per sviluppare questa piccola applicazione web e rendere le operazioni CRUD (Create, Read, Update, Delete) facilmente accessibili.

Cosa non è: un frontend scritto bene, con i controlli di sicurezza e il CORS attivo, non mi sbatto per far contento il Ph.D Griscioli che domattina me le sfragolerà con gli assessment e le compliance.

Cosa è: è un'applicazione scritta in mezza giornata a caffé e panini in **Python (Flask)** riutilizzando altre baseline che già avevo e che usavano **Bootstrap 5**. L'obiettivo era ed è non diventare matto a gestire il database relazionale sottostante (PostgreSQL) e verificare che funzioni perfettamente nel gestire la marea di relazioni tra Organizzazioni, Servizi, Asset e Supply Chain.

## ⚙️ Prerequisiti

Che funzioni il project work SIGNIS_PW_2_19_031400314. Se non sta su un db locale o remoto e non sono stati configurati i parametri d'accesso, l'app non funziona (e ce credo, senza DB a cui collegarsi la vedo dura.).

Quindi, first rule, lanciare lo stack Docker del project work:

```bash
sudo docker compose up -d

```

## 🐑 Clonazione del repository (BEEEEE)

```bash
git clone https://github.com/laverio078/webapp-signis.git

```

## 🚀 First run

Io consiglio l'uso del venv di python per non sporcare il proprio ambiente, però ognuno è libero di fare come gli pare.

Per creare il venv la prassi è questa (prendo per assunto che chi lo usa abbia un linux debian derivato, io ho Mint):

```bash
sudo apt install python3-venv
python3 -m venv ./venv
source ./venv/bin/activate

```

Ovviamente, scegliere una cartella dove creare la cartella venv a proprio piacimento (già ci sto mettendo troppo a scrivere la documentazione).

1. **Entrare nella cartella della webapp** (se non ci sei già):
```bash
cd webapp-signis

```


2. **Installare le due librerie in croce che servono** (Flask e Psycopg2 per parlare col DB):
```bash
pip install -r requirements.txt

```


3. **Avviare l'applicazione**:
```bash
python3 app.py

```


4. **Aprire il browser**:
Vai all'indirizzo [http://localhost:5000] o [http://127.0.0.1:5000].

## 🧰 Cosa si può fare con l'App

L'interfaccia mappa, spero, fedelmente l'infrastruttura del database e permette di:

* **Visualizzare la Dashboard**: Statistiche su quanti asset e servizi (soprattutto quelli *critici*) sono presenti.
* **Gestire le Anagrafiche Base**: Inserimento, modifica e cancellazione dei dati.
* **Gestire il Core NIS2**: Censire Asset e Servizi.
* **Creare le Relazioni**:
* * **Asset x Servizio**: Associare uno o più asset fisici/logici a un servizio aziendale (es. "Il Server X fa da Database per il Servizio Y").
* * **Supply Chain**: Gestire le dipendenze dai fornitori esterni, inserendo riferimenti SLA e tipo di fornitura, come richiesto dall'art. 21 della Direttiva NIS2.
* **Compliance ACN**: Per gestire il tiering e l'implementazione dei controlli di sicurezza secondo il framework CISI/CIN



## 📝 Note Tecniche

* L'app si collega al database con l'utente `admin` e cerca automaticamente i dati nello schema `nis2` tramite l'opzione `options="-c search_path=nis2,public"`.
* I metadati avanzati (come quelli di Persone e Fornitori) vengono salvati su DB in formato `JSONB`. L'interfaccia web accetta stringhe JSON e le passa direttamente al motore di Postgres, quindi essendo dati JSON il campo non può rimanere vuoto ma deve essere riempito con {}.
* L'app potrebbe anche non funzionare correttamente, però sono stati fatti test unitari estensivi.

## 📄 Licenza

Questo progetto è distribuito sotto licenza **GNU General Public License v3.0 (GPL-3.0)**.
Sei libero di usare, studiare, condividere e modificare il software. Qualsiasi progetto derivato dovrà essere distribuito sotto la medesima licenza. 
Per i dettagli completi, consulta il file [LICENSE](LICENSE) presente nella root del repository.
