# Step 27B - Procedimenti Access DDL

## 1. Obiettivo funzionale dell'entita Procedimento

Il Procedimento e un contenitore logico-operativo della piattaforma Soluzioni Operative, introdotto inizialmente nel modulo ProtocolloMonitor.

Serve a raggruppare uno o piu protocolli acquisiti che appartengono alla stessa pratica, lavorazione, istanza, intervento o fascicolo operativo.

Il Procedimento non sostituisce il Protocollo:

- il Protocollo resta l'evento documentale acquisito da Grisù/Vigilia;
- il Procedimento rappresenta la lavorazione complessiva;
- piu protocolli possono concorrere allo stesso Procedimento;
- in futuro un Procedimento potra contenere documenti, tag, metadati, scadenze, soggetti, workflow, audit e permessi.

## 2. Schema MVP consigliato

Schema minimo proposto:

- `T_Procedimenti`: tabella padre del procedimento;
- `T_ProcedimentoProtocolli`: tabella ponte tra procedimenti e protocolli.

La tabella ponte viene proposta gia nell'MVP per evitare di modificare subito `T_Protocolli` e per preparare una relazione futura molti-a-molti.

## 3. DDL Access proposto

### T_Procedimenti

```sql
CREATE TABLE T_Procedimenti (
    IDProcedimento AUTOINCREMENT CONSTRAINT PK_T_Procedimenti PRIMARY KEY,
    CodiceProcedimento TEXT(50),
    Titolo TEXT(255),
    Descrizione LONGTEXT,
    AziendaSoggetto TEXT(255),
    ComandoCompetenza TEXT(50),
    SettoreCompetenza TEXT(100),
    TipologiaProcedimento TEXT(100),
    StatoProcedimento TEXT(50),
    Priorita TEXT(50),
    DataApertura DATETIME,
    DataUltimoAggiornamento DATETIME,
    DataScadenza DATETIME,
    DataChiusura DATETIME,
    NoteInterne LONGTEXT,
    Attivo YESNO,
    DataCreazione DATETIME,
    DataModifica DATETIME
);
```

### T_ProcedimentoProtocolli

```sql
CREATE TABLE T_ProcedimentoProtocolli (
    IDProcedimentoProtocollo AUTOINCREMENT CONSTRAINT PK_T_ProcedimentoProtocolli PRIMARY KEY,
    IDProcedimento LONG,
    IDProtocollo LONG,
    RuoloProtocollo TEXT(50),
    Principale YESNO,
    DataCollegamento DATETIME,
    NoteCollegamento LONGTEXT
);
```

## 4. Campi, tipi dati Access e significato operativo

### T_Procedimenti

| Campo | Tipo Access | Significato operativo |
|---|---:|---|
| `IDProcedimento` | `AUTOINCREMENT` | Chiave tecnica interna del procedimento. |
| `CodiceProcedimento` | `TEXT(50)` | Codice leggibile e stabile, utile per ricerca e UI. |
| `Titolo` | `TEXT(255)` | Titolo sintetico della pratica. |
| `Descrizione` | `LONGTEXT` | Descrizione estesa del procedimento. |
| `AziendaSoggetto` | `TEXT(255)` | Denominazione libera iniziale di azienda, persona, ente o soggetto. |
| `ComandoCompetenza` | `TEXT(50)` | Comando competente, inizialmente testuale. |
| `SettoreCompetenza` | `TEXT(100)` | Settore/ufficio/ambito di competenza. |
| `TipologiaProcedimento` | `TEXT(100)` | Classificazione del procedimento. |
| `StatoProcedimento` | `TEXT(50)` | Stato operativo, ad esempio `NUOVO`, `IN_LAVORAZIONE`, `CHIUSO`. |
| `Priorita` | `TEXT(50)` | Priorita operativa, ad esempio `Bassa`, `Normale`, `Alta`, `Urgente`. |
| `DataApertura` | `DATETIME` | Data di apertura logica del procedimento. |
| `DataUltimoAggiornamento` | `DATETIME` | Ultimo aggiornamento funzionale. |
| `DataScadenza` | `DATETIME` | Scadenza operativa principale. |
| `DataChiusura` | `DATETIME` | Data di chiusura, se presente. |
| `NoteInterne` | `LONGTEXT` | Annotazioni interne non strutturate. |
| `Attivo` | `YESNO` | Soft delete/logica di visibilita. |
| `DataCreazione` | `DATETIME` | Timestamp tecnico di creazione. |
| `DataModifica` | `DATETIME` | Timestamp tecnico di ultima modifica. |

### T_ProcedimentoProtocolli

| Campo | Tipo Access | Significato operativo |
|---|---:|---|
| `IDProcedimentoProtocollo` | `AUTOINCREMENT` | Chiave tecnica della relazione. |
| `IDProcedimento` | `LONG` | Riferimento al procedimento. |
| `IDProtocollo` | `LONG` | Riferimento a `T_Protocolli.IDProtocollo`. |
| `RuoloProtocollo` | `TEXT(50)` | Ruolo del protocollo nel procedimento, ad esempio `APERTURA`, `INTEGRAZIONE`, `CHIUSURA`. |
| `Principale` | `YESNO` | Indica se il protocollo e il principale del procedimento. |
| `DataCollegamento` | `DATETIME` | Data in cui il protocollo e stato collegato. |
| `NoteCollegamento` | `LONGTEXT` | Note specifiche della relazione. |

## 5. Indici consigliati

```sql
CREATE INDEX IX_T_Procedimenti_CodiceProcedimento
ON T_Procedimenti (CodiceProcedimento);

CREATE INDEX IX_T_Procedimenti_AziendaSoggetto
ON T_Procedimenti (AziendaSoggetto);

CREATE INDEX IX_T_Procedimenti_ComandoCompetenza
ON T_Procedimenti (ComandoCompetenza);

CREATE INDEX IX_T_Procedimenti_SettoreCompetenza
ON T_Procedimenti (SettoreCompetenza);

CREATE INDEX IX_T_Procedimenti_StatoProcedimento
ON T_Procedimenti (StatoProcedimento);

CREATE INDEX IX_T_Procedimenti_Priorita
ON T_Procedimenti (Priorita);

CREATE INDEX IX_T_Procedimenti_DataScadenza
ON T_Procedimenti (DataScadenza);

CREATE INDEX IX_T_ProcedimentoProtocolli_IDProcedimento
ON T_ProcedimentoProtocolli (IDProcedimento);

CREATE INDEX IX_T_ProcedimentoProtocolli_IDProtocollo
ON T_ProcedimentoProtocolli (IDProtocollo);

CREATE UNIQUE INDEX UX_T_ProcedimentoProtocolli_Procedimento_Protocollo
ON T_ProcedimentoProtocolli (IDProcedimento, IDProtocollo);
```

## 6. Relazione logica con T_Protocolli

Relazione logica:

```text
T_Procedimenti.IDProcedimento
  -> T_ProcedimentoProtocolli.IDProcedimento

T_Protocolli.IDProtocollo
  -> T_ProcedimentoProtocolli.IDProtocollo
```

Nel modello MVP, un Procedimento puo collegare piu protocolli.

La cardinalita pratica iniziale puo essere trattata come 1:N:

```text
1 Procedimento -> N Protocolli
```

La tabella ponte permette pero di evolvere senza rotture verso N:N:

```text
N Procedimenti <-> N Protocolli
```

## 7. Motivazione della tabella ponte

La tabella ponte e preferibile al campo diretto `IDProcedimento` in `T_Protocolli` per questi motivi:

- non modifica subito la tabella critica `T_Protocolli`;
- riduce il rischio di regressioni sul flusso esistente Flask/Grisù/Access;
- permette di collegare un protocollo a piu procedimenti, se in futuro servira;
- consente di aggiungere metadati della relazione, come `RuoloProtocollo`, `Principale`, `DataCollegamento`;
- e piu vicina al modello PostgreSQL definitivo;
- permette una migrazione graduale: prima relazione esterna, poi eventuale ottimizzazione.

## 8. Note PostgreSQL-friendly

Quando PostgreSQL diventera il target operativo:

- `AUTOINCREMENT` diventera `GENERATED BY DEFAULT AS IDENTITY`;
- `TEXT(50)` e `TEXT(255)` potranno diventare `varchar(50)` e `varchar(255)`;
- `LONGTEXT` diventera `text`;
- `YESNO` diventera `boolean`;
- `DATETIME` diventera `timestamp` o `timestamptz`;
- gli indici potranno essere mantenuti con nomi equivalenti;
- le foreign key potranno essere rese esplicite e vincolanti.

Schema concettuale PostgreSQL futuro:

```sql
procedimenti (
    id_procedimento bigint generated by default as identity primary key,
    codice_procedimento varchar(50),
    titolo varchar(255),
    descrizione text,
    azienda_soggetto varchar(255),
    comando_competenza varchar(50),
    settore_competenza varchar(100),
    tipologia_procedimento varchar(100),
    stato_procedimento varchar(50),
    priorita varchar(50),
    data_apertura timestamptz,
    data_ultimo_aggiornamento timestamptz,
    data_scadenza timestamptz,
    data_chiusura timestamptz,
    note_interne text,
    attivo boolean,
    data_creazione timestamptz,
    data_modifica timestamptz
);

procedimento_protocolli (
    id_procedimento_protocollo bigint generated by default as identity primary key,
    id_procedimento bigint not null references procedimenti(id_procedimento),
    id_protocollo bigint not null,
    ruolo_protocollo varchar(50),
    principale boolean,
    data_collegamento timestamptz,
    note_collegamento text,
    unique (id_procedimento, id_protocollo)
);
```

## 9. Evoluzione futura

### Tag

Tabelle consigliate:

```text
T_Tags
T_EntityTags
```

Con `EntityType = 'procedimento'` e `EntityID = IDProcedimento`.

### Soggetti

Evoluzione da `AziendaSoggetto` testuale verso:

```text
T_Soggetti
T_ProcedimentoSoggetti
```

Questo permettera di gestire aziende, persone fisiche, enti, comuni, proprietari, delegati e altri ruoli.

### Comandi

Evoluzione da `ComandoCompetenza` testuale verso:

```text
L_Comandi
```

Il campo potra diventare un riferimento a codice comando stabile.

### Settori competenza

Evoluzione da `SettoreCompetenza` testuale verso:

```text
L_SettoriCompetenza
```

Questo permettera filtri e statistiche piu affidabili.

### Metadati

Evoluzione verso:

```text
T_MetadataDefinitions
T_EntityMetadataValues
```

Con `EntityType = 'procedimento'`.

## 10. Script VBA Access opzionale

Il seguente script e solo una bozza operativa.

Non deve essere eseguito automaticamente.

Prima dell'uso reale:

1. creare backup del file `.accdb`;
2. verificare nomi tabella gia presenti;
3. eseguire in ambiente di prova;
4. verificare indici e tipi dati.

```vba
Option Compare Database
Option Explicit

Public Sub CreaTabelleProcedimenti_MVP()
    Dim db As DAO.Database
    Set db = CurrentDb

    db.Execute _
        "CREATE TABLE T_Procedimenti (" & _
        "IDProcedimento AUTOINCREMENT CONSTRAINT PK_T_Procedimenti PRIMARY KEY, " & _
        "CodiceProcedimento TEXT(50), " & _
        "Titolo TEXT(255), " & _
        "Descrizione LONGTEXT, " & _
        "AziendaSoggetto TEXT(255), " & _
        "ComandoCompetenza TEXT(50), " & _
        "SettoreCompetenza TEXT(100), " & _
        "TipologiaProcedimento TEXT(100), " & _
        "StatoProcedimento TEXT(50), " & _
        "Priorita TEXT(50), " & _
        "DataApertura DATETIME, " & _
        "DataUltimoAggiornamento DATETIME, " & _
        "DataScadenza DATETIME, " & _
        "DataChiusura DATETIME, " & _
        "NoteInterne LONGTEXT, " & _
        "Attivo YESNO, " & _
        "DataCreazione DATETIME, " & _
        "DataModifica DATETIME" & _
        ")"

    db.Execute _
        "CREATE TABLE T_ProcedimentoProtocolli (" & _
        "IDProcedimentoProtocollo AUTOINCREMENT CONSTRAINT PK_T_ProcedimentoProtocolli PRIMARY KEY, " & _
        "IDProcedimento LONG, " & _
        "IDProtocollo LONG, " & _
        "RuoloProtocollo TEXT(50), " & _
        "Principale YESNO, " & _
        "DataCollegamento DATETIME, " & _
        "NoteCollegamento LONGTEXT" & _
        ")"

    db.Execute "CREATE INDEX IX_T_Procedimenti_CodiceProcedimento ON T_Procedimenti (CodiceProcedimento)"
    db.Execute "CREATE INDEX IX_T_Procedimenti_AziendaSoggetto ON T_Procedimenti (AziendaSoggetto)"
    db.Execute "CREATE INDEX IX_T_Procedimenti_ComandoCompetenza ON T_Procedimenti (ComandoCompetenza)"
    db.Execute "CREATE INDEX IX_T_Procedimenti_SettoreCompetenza ON T_Procedimenti (SettoreCompetenza)"
    db.Execute "CREATE INDEX IX_T_Procedimenti_StatoProcedimento ON T_Procedimenti (StatoProcedimento)"
    db.Execute "CREATE INDEX IX_T_Procedimenti_Priorita ON T_Procedimenti (Priorita)"
    db.Execute "CREATE INDEX IX_T_Procedimenti_DataScadenza ON T_Procedimenti (DataScadenza)"
    db.Execute "CREATE INDEX IX_T_ProcedimentoProtocolli_IDProcedimento ON T_ProcedimentoProtocolli (IDProcedimento)"
    db.Execute "CREATE INDEX IX_T_ProcedimentoProtocolli_IDProtocollo ON T_ProcedimentoProtocolli (IDProtocollo)"
    db.Execute "CREATE UNIQUE INDEX UX_T_ProcedimentoProtocolli_Procedimento_Protocollo ON T_ProcedimentoProtocolli (IDProcedimento, IDProtocollo)"

    MsgBox "Tabelle Procedimenti create. Verificare struttura e indici.", vbInformation
End Sub
```

## 11. Regola di sicurezza backup

Prima di ogni futura modifica reale al file `.accdb` deve essere creata una copia di backup con data e ora nel nome file.

Formato consigliato:

```text
ProtocolloMonitor_YYYYMMDD_HHMMSS.accdb
```

Esempio:

```text
ProtocolloMonitor_20260525_153000.accdb
```

La modifica reale non deve iniziare se il backup non esiste o non e stato verificato.

## 12. Rollback manuale

Rollback minimo se lo schema viene creato in prova e deve essere rimosso:

```sql
DROP TABLE T_ProcedimentoProtocolli;
DROP TABLE T_Procedimenti;
```

Nota:

- rimuovere prima la tabella ponte;
- verificare eventuali relazioni Access create manualmente;
- verificare eventuali query, maschere o report Access collegati;
- se ci sono dati reali, esportarli prima di cancellare.

Rollback piu sicuro:

1. chiudere tutti i runtime;
2. ripristinare il file `.accdb` dal backup creato prima dell'intervento;
3. riaprire Access e verificare integrita;
4. riavviare FastAPI/Flask solo dopo verifica.

## 13. Checklist di validazione prima dell'esecuzione reale

Prima di eseguire qualunque DDL reale:

- [ ] Il file `.accdb` e chiuso da Access, FastAPI, Flask e altri processi.
- [ ] E stata creata copia backup con data e ora nel nome file.
- [ ] Il backup e stato aperto/verificato o almeno copiato correttamente.
- [ ] Le tabelle `T_Procedimenti` e `T_ProcedimentoProtocolli` non esistono gia.
- [ ] I nomi campo non confliggono con convenzioni Access esistenti.
- [ ] Il DDL e stato provato su copia del database.
- [ ] Gli indici sono stati creati senza errori.
- [ ] La tabella `T_Protocolli` non viene modificata in questo step.
- [ ] Non vengono importati dati reali senza piano di rollback.
- [ ] Il backend FastAPI continua a leggere protocolli/PDF/metadata.
- [ ] Il flusso Flask/Grisù continua ad acquisire protocolli.
- [ ] Il frontend Vue continua a visualizzare elenco e dettaglio.

