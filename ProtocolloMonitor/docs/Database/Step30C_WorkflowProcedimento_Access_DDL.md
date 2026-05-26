# Step 30C - Workflow Procedimento Access DDL

## 1. Obiettivo funzionale

Questo documento progetta lo schema Access MVP per rendere persistente il workflow del procedimento introdotto come mock frontend nello Step 30B.

Il workflow deve permettere di gestire:

- fasi del procedimento;
- sottofasi operative dentro ogni fase;
- catalogo riusabile di sottofasi;
- stati di avanzamento fase/sottofase;
- icone e colori usati dal frontend Vue/Vuetify;
- futura evoluzione verso workflow template, utenti responsabili e storico eventi.

Il documento e solo progettuale-operativo: non esegue DDL e non modifica il database reale.

## 2. Relazione con T_Procedimenti

La tabella gia esistente `T_Procedimenti` resta l'aggregatore principale.

Relazione logica MVP:

```text
T_Procedimenti.IDProcedimento
  -> T_ProcedimentoFasi.IDProcedimento
      -> T_ProcedimentoSottofasi.IDFase
          -> L_CatalogoSottofasi.IDCatalogoSottofase opzionale
```

Una fase appartiene a un solo procedimento.

Una sottofase appartiene a una sola fase.

Il catalogo sottofasi e riusabile: descrive modelli di sottofase che possono essere copiati o referenziati nelle sottofasi reali.

## 3. Schema MVP consigliato

Tabelle MVP:

- `T_ProcedimentoFasi`
- `T_ProcedimentoSottofasi`
- `L_CatalogoSottofasi`

Scelta architetturale:

- `T_ProcedimentoFasi` contiene le fasi reali di un procedimento.
- `T_ProcedimentoSottofasi` contiene le sottofasi reali di una fase.
- `L_CatalogoSottofasi` contiene voci riusabili per la tendina/avatar del frontend.

Lo schema evita di modificare `T_Procedimenti` e resta compatibile con una futura migrazione PostgreSQL.

## 4. DDL Access proposto

### T_ProcedimentoFasi

```sql
CREATE TABLE T_ProcedimentoFasi (
    IDFase AUTOINCREMENT CONSTRAINT PK_T_ProcedimentoFasi PRIMARY KEY,
    IDProcedimento LONG,
    CodiceFase TEXT(50),
    Titolo TEXT(255),
    Descrizione LONGTEXT,
    Ordine INTEGER,
    StatoFase TEXT(50),
    Responsabile TEXT(255),
    DataScadenza DATETIME,
    DataAvvio DATETIME,
    DataCompletamento DATETIME,
    Obbligatoria YESNO,
    Bloccante YESNO,
    Attivo YESNO,
    DataCreazione DATETIME,
    DataModifica DATETIME
);
```

### T_ProcedimentoSottofasi

```sql
CREATE TABLE T_ProcedimentoSottofasi (
    IDSottofase AUTOINCREMENT CONSTRAINT PK_T_ProcedimentoSottofasi PRIMARY KEY,
    IDFase LONG,
    IDCatalogoSottofase LONG,
    CodiceSottofase TEXT(50),
    Titolo TEXT(255),
    Descrizione LONGTEXT,
    Ordine INTEGER,
    StatoSottofase TEXT(50),
    Icona TEXT(100),
    Colore TEXT(50),
    Responsabile TEXT(255),
    DataScadenza DATETIME,
    DataAvvio DATETIME,
    DataCompletamento DATETIME,
    NoteInterne LONGTEXT,
    Attivo YESNO,
    DataCreazione DATETIME,
    DataModifica DATETIME
);
```

### L_CatalogoSottofasi

```sql
CREATE TABLE L_CatalogoSottofasi (
    IDCatalogoSottofase AUTOINCREMENT CONSTRAINT PK_L_CatalogoSottofasi PRIMARY KEY,
    CodiceSottofase TEXT(50),
    Titolo TEXT(255),
    Descrizione LONGTEXT,
    Icona TEXT(100),
    Colore TEXT(50),
    Categoria TEXT(100),
    OrdineDefault INTEGER,
    Attivo YESNO,
    DataCreazione DATETIME,
    DataModifica DATETIME
);
```

## 5. Campi, tipi dati Access e significato operativo

### T_ProcedimentoFasi

| Campo | Tipo Access | Significato operativo |
| --- | --- | --- |
| `IDFase` | `AUTOINCREMENT` | Chiave primaria tecnica della fase. |
| `IDProcedimento` | `LONG` | Riferimento a `T_Procedimenti.IDProcedimento`. |
| `CodiceFase` | `TEXT(50)` | Codice stabile della fase, utile per template e ricerca. |
| `Titolo` | `TEXT(255)` | Titolo visualizzato nella timeline verticale. |
| `Descrizione` | `LONGTEXT` | Descrizione operativa della fase. |
| `Ordine` | `INTEGER` | Posizione della fase nel workflow del procedimento. |
| `StatoFase` | `TEXT(50)` | Stato corrente della fase. |
| `Responsabile` | `TEXT(255)` | Responsabile testuale provvisorio. |
| `DataScadenza` | `DATETIME` | Scadenza operativa della fase. |
| `DataAvvio` | `DATETIME` | Data/ora di avvio fase. |
| `DataCompletamento` | `DATETIME` | Data/ora di completamento fase. |
| `Obbligatoria` | `YESNO` | Indica se la fase e obbligatoria. |
| `Bloccante` | `YESNO` | Indica se la fase blocca avanzamenti successivi. |
| `Attivo` | `YESNO` | Flag conservativo per disattivazione logica. |
| `DataCreazione` | `DATETIME` | Data creazione record. |
| `DataModifica` | `DATETIME` | Data ultima modifica record. |

### T_ProcedimentoSottofasi

| Campo | Tipo Access | Significato operativo |
| --- | --- | --- |
| `IDSottofase` | `AUTOINCREMENT` | Chiave primaria tecnica della sottofase. |
| `IDFase` | `LONG` | Riferimento a `T_ProcedimentoFasi.IDFase`. |
| `IDCatalogoSottofase` | `LONG` | Riferimento opzionale al catalogo origine. |
| `CodiceSottofase` | `TEXT(50)` | Codice stabile della sottofase. |
| `Titolo` | `TEXT(255)` | Titolo visualizzato sotto l'avatar. |
| `Descrizione` | `LONGTEXT` | Descrizione operativa. |
| `Ordine` | `INTEGER` | Posizione orizzontale nella fase. |
| `StatoSottofase` | `TEXT(50)` | Stato corrente della sottofase. |
| `Icona` | `TEXT(100)` | Nome icona MDI usata dal frontend. |
| `Colore` | `TEXT(50)` | Colore Vuetify/avatar suggerito. |
| `Responsabile` | `TEXT(255)` | Responsabile testuale provvisorio. |
| `DataScadenza` | `DATETIME` | Scadenza sottofase. |
| `DataAvvio` | `DATETIME` | Data/ora di avvio sottofase. |
| `DataCompletamento` | `DATETIME` | Data/ora completamento sottofase. |
| `NoteInterne` | `LONGTEXT` | Note operative interne. |
| `Attivo` | `YESNO` | Flag conservativo per disattivazione logica. |
| `DataCreazione` | `DATETIME` | Data creazione record. |
| `DataModifica` | `DATETIME` | Data ultima modifica record. |

### L_CatalogoSottofasi

| Campo | Tipo Access | Significato operativo |
| --- | --- | --- |
| `IDCatalogoSottofase` | `AUTOINCREMENT` | Chiave primaria tecnica del catalogo. |
| `CodiceSottofase` | `TEXT(50)` | Codice riusabile e potenzialmente univoco. |
| `Titolo` | `TEXT(255)` | Titolo mostrato nella tendina. |
| `Descrizione` | `LONGTEXT` | Descrizione mostrata nella tendina. |
| `Icona` | `TEXT(100)` | Icona MDI default. |
| `Colore` | `TEXT(50)` | Colore default avatar. |
| `Categoria` | `TEXT(100)` | Categoria logica futura. |
| `OrdineDefault` | `INTEGER` | Ordinamento suggerito nel catalogo. |
| `Attivo` | `YESNO` | Mostra/nasconde voce catalogo. |
| `DataCreazione` | `DATETIME` | Data creazione voce catalogo. |
| `DataModifica` | `DATETIME` | Data ultima modifica voce catalogo. |

## 6. Indici consigliati

```sql
CREATE INDEX IX_T_ProcedimentoFasi_IDProcedimento
ON T_ProcedimentoFasi (IDProcedimento);

CREATE INDEX IX_T_ProcedimentoFasi_StatoFase
ON T_ProcedimentoFasi (StatoFase);

CREATE INDEX IX_T_ProcedimentoFasi_Ordine
ON T_ProcedimentoFasi (IDProcedimento, Ordine);

CREATE INDEX IX_T_ProcedimentoFasi_DataScadenza
ON T_ProcedimentoFasi (DataScadenza);

CREATE INDEX IX_T_ProcedimentoSottofasi_IDFase
ON T_ProcedimentoSottofasi (IDFase);

CREATE INDEX IX_T_ProcedimentoSottofasi_StatoSottofase
ON T_ProcedimentoSottofasi (StatoSottofase);

CREATE INDEX IX_T_ProcedimentoSottofasi_Ordine
ON T_ProcedimentoSottofasi (IDFase, Ordine);

CREATE INDEX IX_T_ProcedimentoSottofasi_IDCatalogoSottofase
ON T_ProcedimentoSottofasi (IDCatalogoSottofase);

CREATE UNIQUE INDEX UX_L_CatalogoSottofasi_CodiceSottofase
ON L_CatalogoSottofasi (CodiceSottofase);

CREATE INDEX IX_L_CatalogoSottofasi_Attivo
ON L_CatalogoSottofasi (Attivo);
```

## 7. Regole logiche

Regole principali:

- una fase appartiene a un procedimento;
- una sottofase appartiene a una fase;
- il catalogo e riusabile;
- una sottofase reale puo derivare dal catalogo ma deve poter conservare titolo, descrizione, icona e colore copiati al momento della creazione;
- gli stati sono salvati come testo per restare compatibili con Access e facilmente migrabili in PostgreSQL.

Stati ammessi:

```text
NON_AVVIATA
IN_CORSO
COMPLETATA
BLOCCATA
SCADUTA
SOSPESA
```

Regole consigliate:

- `Ordine` deve essere valorizzato per mantenere timeline e stepper stabili.
- `Attivo = True` per record operativi.
- `DataCompletamento` dovrebbe essere valorizzata quando lo stato diventa `COMPLETATA`.
- `DataAvvio` dovrebbe essere valorizzata quando lo stato passa a `IN_CORSO`.
- Il frontend non deve assumere che le fasi siano sempre tre: il workflow deve essere variabile.

## 8. Note PostgreSQL-friendly

Lo schema e preparato per PostgreSQL perche:

- usa chiavi surrogate (`IDFase`, `IDSottofase`, `IDCatalogoSottofase`);
- separa fasi, sottofasi e catalogo;
- non usa campi multivalore Access;
- non serializza strutture JSON dentro colonne testo;
- mantiene stati come codici testuali stabili;
- consente in futuro vincoli `FOREIGN KEY`, `CHECK` e indici parziali.

Migrazione futura suggerita:

- `IDFase` -> `id_fase BIGSERIAL`;
- `IDProcedimento` -> `id_procedimento BIGINT`;
- `YESNO` -> `BOOLEAN`;
- `DATETIME` -> `TIMESTAMP`;
- stati -> `CHECK` oppure tabella lookup;
- icone/colori -> campi testuali o configurazione frontend controllata.

## 9. Relazione futura con tipologia procedimento

Oggi il workflow puo essere creato direttamente per ogni procedimento.

In futuro, `TipologiaProcedimento` potra determinare un template di workflow:

```text
TipologiaProcedimento
  -> WorkflowTemplate
      -> FasiTemplate
          -> SottofasiTemplate
```

Quando un procedimento viene creato, le fasi template potranno essere copiate in `T_ProcedimentoFasi` e le sottofasi template in `T_ProcedimentoSottofasi`.

Questo evita che tutti i procedimenti abbiano lo stesso workflow rigido.

## 10. Possibile evoluzione verso workflow template

Tabelle future possibili:

- `T_WorkflowTemplate`
- `T_WorkflowTemplateFasi`
- `T_WorkflowTemplateSottofasi`

Il template descrive il modello.

Le tabelle `T_ProcedimentoFasi` e `T_ProcedimentoSottofasi` restano invece istanze operative reali, modificabili e storicizzabili per il singolo procedimento.

## 11. Possibile relazione con utenti/responsabili

Nel MVP `Responsabile` resta testo libero per ridurre complessita e dipendenze.

In una fase successiva, quando autenticazione/ruoli saranno introdotti, potranno essere aggiunti:

- `IDUtenteResponsabile`;
- `IDGruppoResponsabile`;
- tabella utenti;
- tabella gruppi;
- permessi per avanzare/completare/bloccare fasi.

La transizione consigliata e mantenere temporaneamente sia il campo testuale sia l'ID utente/gruppo, poi deprecare il testo libero.

## 12. Possibile relazione con log eventi/storico

Il cambio stato di fasi e sottofasi dovrebbe generare eventi applicativi.

Tabella futura possibile:

```text
T_WorkflowEventi
  IDEvento
  EntityType
  EntityID
  StatoPrecedente
  StatoNuovo
  Azione
  UserID
  RequestID
  DataEvento
  Note
```

Questa evoluzione si collega al logging strutturato gia introdotto nel backend e prepara audit, workflow multiutente e tracciabilita.

## 13. Rollback manuale

Rollback preferito:

1. chiudere Access;
2. ripristinare il file `.accdb` dal backup creato prima dell'intervento;
3. riaprire il database ripristinato;
4. verificare che `T_Procedimenti` e `T_ProcedimentoProtocolli` siano ancora presenti;
5. verificare che backend e frontend funzionino come prima.

Rollback SQL manuale, solo se non ci sono dati da conservare:

```sql
DROP TABLE T_ProcedimentoSottofasi;
DROP TABLE T_ProcedimentoFasi;
DROP TABLE L_CatalogoSottofasi;
```

Ordine importante:

1. eliminare prima `T_ProcedimentoSottofasi`;
2. eliminare poi `T_ProcedimentoFasi`;
3. eliminare infine `L_CatalogoSottofasi`.

Se in Access saranno create relazioni manuali, rimuoverle prima del `DROP TABLE`.

## 14. Checklist prima dell'esecuzione reale

Prima di eseguire DDL reale:

- [ ] Il file `.accdb` e chiuso da Access, FastAPI, Flask e altri processi.
- [ ] Non esiste file `.laccdb` accanto al database.
- [ ] Il database non e bloccato da OneDrive, antivirus o sincronizzatori.
- [ ] E stata individuata la copia runtime corretta del database.
- [ ] E stata creata una copia di backup con timestamp.
- [ ] Il backup e stato verificato come file esistente.
- [ ] Lo script DDL e stato provato prima su copia del database.
- [ ] I nomi tabella non confliggono con tabelle esistenti.
- [ ] I nomi campo non confliggono con convenzioni Access esistenti.
- [ ] `T_Procedimenti` non viene modificata.
- [ ] `T_ProcedimentoProtocolli` non viene modificata.
- [ ] Backend e frontend sono fermi o in condizione controllata.

## 15. Regola obbligatoria backup

Prima di qualsiasi modifica reale al file `.accdb` deve essere creato un backup con timestamp.

Formato consigliato:

```text
Backup\ProtocolloMonitor_BACKUP_YYYYMMDD_HHMMSS.accdb
```

Se il backup fallisce, nessuna modifica deve essere eseguita.

La creazione delle tabelle workflow deve partire solo dopo avere verificato che:

- la cartella `Backup` esiste;
- il file backup esiste;
- il file backup ha dimensione coerente;
- non esiste file `.laccdb`;
- il database operativo e quello corretto.
