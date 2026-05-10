# PROMEMORIA ARCHITETTURALE – ProtocolloMonitor Evoluzione Documentale

## Visione generale

L’obiettivo NON è creare un semplice archivio file.

L’obiettivo è creare una piattaforma documentale operativa collaborativa che:
- centralizzi i documenti
- elimini duplicazioni
- renda tracciabili le lavorazioni
- migliori la collaborazione tra uffici e colleghi
- riduca l’utilizzo caotico delle e-mail
- mantenga chiara la responsabilità operativa
- sia semplice da usare
- sia scalabile nel tempo

---

# PRINCIPIO FONDAMENTALE

```text
Filesystem = storage fisico
Database = organizzazione logica
Piattaforma = governance operativa
```

Il filesystem NON rappresenta più:
- pratiche
- lavorazioni
- utenti
- organizzazione logica

Serve solo per conservare i file.

---

# DOCUMENTO UNICO

Regola fondamentale:

```text
Un documento PDF deve esistere una sola volta
```

Mai duplicare file.

Se più utenti lavorano sullo stesso documento:
- il file resta unico
- cambiano solo i collegamenti nel database

---

# NAMING FILE DEFINITIVO

Si è deciso di NON inserire metadati complessi nel nome file.

Motivazione:
- i metadati sono già nel database
- il filename deve essere stabile e corto
- il database governa la ricerca

Formato definitivo:

```text
[Tipo]_[ComandoVigilia]_[Protocollo]_[Data].pdf
```

Esempio:

```text
E_DIR-SIC_12332_20260512.pdf
```

Dove:
- E/U = Entrata/Uscita
- DIR-SIC = comando Vigilia
- 12332 = protocollo
- 20260512 = data ISO

---

# STRUTTURA STORAGE FISICO

Cartelle solo per distribuzione fisica:

```text
\FILESERVER\ProtocolloMonitor\Documenti\2026\05\
```

oppure:

```text
\FILESERVER\ProtocolloMonitor\Documenti\2026\05\12\
```

Le cartelle NON rappresentano:
- utenti
- pratiche
- lavorazioni

---

# MULTIUTENZA

Il sistema dovrà essere multiutente.

MA:
- semplice all’inizio
- senza workflow complessi

---

# REGOLA ACCESSO DOCUMENTI

Un utente può accedere a un documento SOLO se:

```text
1) lo acquisisce da Vigilia tramite Grisù
oppure
2) il documento gli viene condiviso
```

---

# FONTI ACCESSO

```text
VIGILIA
CONDIVISIONE
```

---

# CONDIVISIONE DOCUMENTI

La condivisione:
- NON duplica il file
- crea un diritto di accesso
- deve essere tracciata

Esempio:

```text
Francesco condivide documento 12332 con Mario
```

Il sistema deve registrare:
- chi condivide
- a chi
- quando
- con quale permesso

---

# PROCEDIMENTO

Il termine “Lavorazione” è stato ritenuto ambiguo.

Il termine corretto è:

```text
Procedimento
```

Perché rappresenta:
- un iter amministrativo
- più protocolli collegati
- più documenti
- evoluzione temporale
- relazioni tra note

---

# MODELLO CONCETTUALE

```text
Procedimento
↓
contiene molti Documenti
↓
i documenti possono essere collegati tra loro
↓
gli utenti lavorano sul procedimento
```

---

# ESEMPIO REALE PROCEDIMENTO

Procedimento:

```text
Pulizia straordinaria Siracusa
```

Documenti:
1. richiesta preventivo Siracusa
2. richiesta Ciclat
3. preventivo Ciclat
4. approvazione Direzione

Ogni documento:
- cita protocolli precedenti
- genera nuove note
- partecipa ad un flusso ricorsivo

---

# IMPORTANTE

```text
Il procedimento sopravvive ai singoli protocolli
```

Il documento è un evento del procedimento.

---

# LAVORAZIONI UTENTE

Ogni utente può:
- seguire procedimenti
- collegare documenti
- annotare stati
- creare note operative

Ma inizialmente:

```text
una lavorazione/procedimento appartiene a un solo utente
```

La collaborazione multiutente avanzata sarà futura.

---

# CONDIVISIONE OPERATIVA

Un utente può:
- condividere un documento
- senza perdere responsabilità
- senza trasferire proprietà

Possibili ruoli:
- Responsabile
- Collaboratore
- Lettore
- Firmatario
- Supervisore

---

# SICUREZZA

Regola fondamentale:

```text
gli utenti NON devono accedere direttamente alle cartelle documentali
```

Accesso solo tramite piattaforma.

Architettura:

```text
Utente
↓
Frontend Vue
↓
FastAPI
↓
Controllo permessi
↓
Storage PDF protetto
```

---

# AUDIT LOG

Tutto deve essere tracciato:
- acquisizione
- visualizzazione
- download
- condivisione
- modifica
- firma
- protocollazione
- eliminazione
- chiusura procedimento

---

# PROBLEMA ORGANIZZATIVO REALE

Situazione attuale:
- cartelle personali
- naming personali
- e-mail incontrollate
- duplicazioni
- organizzazione individuale
- perdita conoscenza

---

# OBIETTIVO REALE

```text
trasformare pratiche individuali implicite
in processi condivisi e tracciabili
```

---

# RISCHIO PRINCIPALE

Il rischio NON è tecnico.

Il rischio è:

```text
creare un sistema troppo rigido
```

Perché:
- gli utenti lo aggirerebbero
- tornerebbero alle cartelle personali
- tornerebbero alle e-mail

---

# STRATEGIA CORRETTA

NON costruire subito il sistema enterprise completo.

Costruire:

```text
un nucleo minimo estremamente utile
```

che:
- faccia risparmiare tempo
- aiuti concretamente
- venga adottato spontaneamente
- produca dati reali
- permetta evoluzione graduale

---

# MVP CORRETTO

## FARE
- documento unico
- acquisizione Grisù
- procedimenti semplici
- condivisione semplice
- ricerca potente
- timeline procedimento

## NON FARE ORA
- workflow complessi
- permessi ultra granulari
- firma digitale avanzata
- task sofisticati
- automazioni complesse
- versioning evoluto

---

# ARCHITETTURA TECNICA CONSIGLIATA

```text
Vue + Vuetify
↓
FastAPI
↓
PostgreSQL
↓
Storage PDF centralizzato
```

Access è utile per:
- prototipazione
- sperimentazione iniziale

Ma NON sarà sufficiente per:
- centinaia utenti
- permessi complessi
- audit esteso
- ricerca avanzata
- workflow evoluti

---

# OBIETTIVO FINALE

```text
Creare uno strumento che i colleghi vogliono usare,
non uno strumento che devono usare.
```