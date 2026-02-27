**Piano di Studio: Imparare Docker**

---

### Prerequisiti
- Conoscenze base della riga di comando (bash o terminale)
- Concetti base di Linux (file system, processi)
- Fondamentali di networking (concetti base come porte e indirizzi IP)
- Nozioni base di sviluppo software o scripting (es. Python, Node.js o simili)

---

### Step principali

1. **Introduzione a Docker e concetti fondamentali**
2. **Installazione e configurazione di Docker**
3. **Creazione e gestione di container**
4. **Gestione delle immagini Docker**
5. **Dockerfile e automazione della build**
6. **Networking e volumi in Docker**

---

### Micro-step giornalieri (1 settimana)

**Giorno 1:**
- Leggi cos’è Docker e perché si usa (container vs macchina virtuale)
- Guarda un video introduttivo su Docker (20 minuti)
- Installa Docker sul tuo PC

**Giorno 2:**
- Familiarizza con i comandi base: `docker run`, `docker ps`, `docker stop`, `docker rm`
- Esegui il primo container ufficiale (es. `hello-world` e `nginx`)

**Giorno 3:**
- Approfondisci il ciclo di vita di un container
- Impara a gestire i container (start, stop, pause, kill)
- Prova a cancellare container e immagini inutilizzate

**Giorno 4:**
- Scopri cos’è un’immagine Docker e come funziona un repository
- Impara a scaricare immagini dal Docker Hub e a creare immagini custom semplici

**Giorno 5:**
- Impara a scrivere un Dockerfile semplice (es. app Python o Node.js minimale)
- Costruisci l’immagine a partire dal Dockerfile con `docker build`

**Giorno 6:**
- Studio dei volumi Docker per persistenza dei dati
- Esempio pratico: collegare un volume a un container

**Giorno 7:**
- Scopri il networking di base in Docker (bridge network)
- Prova a collegare due container in rete (es. client e server)

---

### Esercizi pratici

1. **Esegui un container interattivo** utilizzando l’immagine `ubuntu` e prova a navigare il file system dal terminale.
2. **Costruisci una immagine Docker** partendo da un semplice Dockerfile che esegue uno script Python “Hello World”.
3. **Crea e collega due container** (es. uno con un server web e uno con un client che fa richieste HTTP).
4. **Usa un volume** per salvare dati persistenti generati da un container (es. file di log o database locale).
5. **Pulisci il sistema Docker** rimuovendo immagini e container inutilizzati e controlla lo spazio liberato.

---

### Verifica finale

- Sei in grado di spiegare a parole semplici cos’è Docker e a cosa serve?
- Riesci a installare Docker e a far partire un container da un’immagine ufficiale?
- Sai scrivere un Dockerfile base e costruire un’immagine a partire da questo?
- Sai collegare container fra loro tramite il networking Docker?
- Sei capace di usare volumi per la persistenza dei dati?
- Sai effettuare operazioni di pulizia in Docker per gestire spazio e risorse?

Se rispondi “sì” a tutte queste domande e riesci a completare gli esercizi senza difficoltà, significa che hai imparato le basi di Docker in modo solido e pratico.