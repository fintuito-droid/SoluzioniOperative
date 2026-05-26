# Step 30L-1 - Schema Access Sottofase Documentale

## 1. Obiettivo funzionale

Questo documento definisce lo schema Access proposto per trasformare la sottofase del workflow procedimento in una sottofase documentale, mantenendo il ruolo operativo gia introdotto in ProtocolloMonitor.

La sottofase continua a rappresentare una lavorazione concreta dentro una fase del procedimento, ad esempio `DOCUMENTO`, `EMAIL`, `FIRMA` o `CONTROLLO`. In aggiunta, puo gestire un ciclo interno fisso:

1. `REDIGI`
2. `REVISIONA`
3. `FIRMA`
4. `PROTOCOLLA`
5. `FINE`

Lo scopo non e sostituire il workflow principale, ma aggiungere una tracciabilita piu fine per le sottofasi che producono o gestiscono documenti, in particolare file Word.

Il modello deve permettere:

- documento Word collegato alla sottofase;
- piu documenti o versioni nel tempo;
- note/testo libero dell'operatore;
- storico dell'avanzamento interno;
- step interni documentali;
- data/ora creazione;
- data/ora ultima azione;
- utente ultima azione;
- stato generale della sottofase;
- riferimento al documento corrente.

## 2. Principio di modellazione

La sottofase resta l'unita operativa visibile nel frontend.

Gli step interni sono invece il dettaglio documentale della sottofase. Questo evita di creare sottofasi artificiali come `Redigi documento`, `Revisiona documento`, `Firma documento`, `Protocolla documento`, che renderebbero piu confusa la timeline.

Schema logico:

```text
T_Procedimenti
  -> T_ProcedimentoFasi
      -> T_ProcedimentoSottofasi
          -> T_SottofaseStepOperativi
          -> T_SottofaseDocumenti
```

## 3. Estensione T_ProcedimentoSottofasi

La tabella `T_ProcedimentoSottofasi` esiste gia e contiene le sottofasi operative del workflow procedimento.

Lo schema proposto prevede l'aggiunta prudente dei seguenti campi.

```sql
ALTER TABLE T_ProcedimentoSottofasi
ADD COLUMN StepCorrente TEXT(50);

ALTER TABLE T_ProcedimentoSottofasi
ADD COLUMN TestoOperatore MEMO;

ALTER TABLE T_ProcedimentoSottofasi
ADD COLUMN HaDocumentoCollegato YESNO;

ALTER TABLE T_ProcedimentoSottofasi
ADD COLUMN IDDocumentoCorrente LONG;

ALTER TABLE T_ProcedimentoSottofasi
ADD COLUMN DataUltimaAzione DATETIME;

ALTER TABLE T_ProcedimentoSottofasi
ADD COLUMN UtenteUltimaAzione TEXT(100);

ALTER TABLE T_ProcedimentoSottofasi
ADD COLUMN VersioneDocumento INTEGER;
```

### Campi aggiunti

| Campo | Tipo Access | Significato operativo |
| --- | --- | --- |
| `StepCorrente` | `TEXT(50)` | Step documentale corrente della sottofase. Valori previsti: `REDIGI`, `REVISIONA`, `FIRMA`, `PROTOCOLLA`, `FINE`. |
| `TestoOperatore` | `MEMO` | Note o testo libero inserito dall'operatore durante la lavorazione della sottofase. |
| `HaDocumentoCollegato` | `YESNO` | Flag rapido per il frontend: indica se esiste almeno un documento collegato alla sottofase. |
| `IDDocumentoCorrente` | `LONG` | Riferimento opzionale al documento attivo/corrente in `T_SottofaseDocumenti`. |
| `DataUltimaAzione` | `DATETIME` | Data e ora dell'ultima azione significativa eseguita sulla sottofase. |
| `UtenteUltimaAzione` | `TEXT(100)` | Identificativo testuale dell'utente che ha eseguito l'ultima azione. Provvisorio fino all'introduzione del sistema utenti/ruoli. |
| `VersioneDocumento` | `INTEGER` | Numero versione corrente del documento principale della sottofase. Campo utile ma opzionale; puo restare nullo per sottofasi non documentali. |

### Note sui campi aggiunti

`StepCorrente` fotografa lo stato sintetico della lavorazione documentale. Lo storico puntuale resta nella tabella `T_SottofaseStepOperativi`.

`HaDocumentoCollegato` e una denormalizzazione leggera pensata per UI e performance. In PostgreSQL potra essere sostituita da vista, computed field o query aggregata.

`IDDocumentoCorrente` evita di dover cercare ogni volta l'ultimo documento attivo quando il frontend deve mostrare l'icona Word o aprire il documento corrente.

`VersioneDocumento` e da considerare un campo di compatibilita MVP. Il versioning reale resta piu robusto se gestito nella tabella documenti.

## 4. Nuova tabella T_SottofaseDocumenti

La tabella `T_SottofaseDocumenti` conserva i documenti collegati a una sottofase. Serve a tracciare file Word, eventuali PDF generati, allegati o versioni successive.

```sql
CREATE TABLE T_SottofaseDocumenti (
    IDDocumentoSottofase COUNTER CONSTRAINT PK_T_SottofaseDocumenti PRIMARY KEY,
    IDSottofase LONG,
    TipoDocumento TEXT(50),
    NomeFile TEXT(255),
    Estensione TEXT(20),
    PercorsoDocumento MEMO,
    MimeType TEXT(100),
    DimensioneBytes LONG,
    HashFile TEXT(128),
    VersioneDocumento INTEGER,
    DataCollegamento DATETIME,
    UtenteCollegamento TEXT(100),
    Attivo YESNO,
    DataCreazione DATETIME,
    DataModifica DATETIME
);
```

### Campi T_SottofaseDocumenti

| Campo | Tipo Access | Significato operativo |
| --- | --- | --- |
| `IDDocumentoSottofase` | `COUNTER` | Chiave primaria tecnica del documento collegato. |
| `IDSottofase` | `LONG` | Riferimento a `T_ProcedimentoSottofasi.IDSottofase`. |
| `TipoDocumento` | `TEXT(50)` | Categoria del documento: ad esempio `WORD`, `PDF`, `ALLEGATO`, `ALTRO`. |
| `NomeFile` | `TEXT(255)` | Nome file visualizzato all'utente. |
| `Estensione` | `TEXT(20)` | Estensione normalizzata, ad esempio `.docx`, `.doc`, `.pdf`. |
| `PercorsoDocumento` | `MEMO` | Percorso assoluto, UNC o relativo gestito dal backend. Si usa `MEMO` per non essere vincolati a 255 caratteri. |
| `MimeType` | `TEXT(100)` | Tipo MIME, ad esempio `application/vnd.openxmlformats-officedocument.wordprocessingml.document`. |
| `DimensioneBytes` | `LONG` | Dimensione del file al momento del collegamento, se disponibile. |
| `HashFile` | `TEXT(128)` | Hash opzionale per rilevare duplicati o verificare integrita. |
| `VersioneDocumento` | `INTEGER` | Numero versione del documento nella sottofase. |
| `DataCollegamento` | `DATETIME` | Data e ora in cui il documento e stato collegato alla sottofase. |
| `UtenteCollegamento` | `TEXT(100)` | Utente che ha collegato il documento. Provvisorio fino all'autenticazione reale. |
| `Attivo` | `YESNO` | Indica se il documento e quello utilizzabile o se e una versione storica/disattivata. |
| `DataCreazione` | `DATETIME` | Data creazione record. |
| `DataModifica` | `DATETIME` | Data ultima modifica record. |

### Indici consigliati T_SottofaseDocumenti

```sql
CREATE INDEX IX_T_SottofaseDocumenti_IDSottofase
ON T_SottofaseDocumenti (IDSottofase);

CREATE INDEX IX_T_SottofaseDocumenti_TipoDocumento
ON T_SottofaseDocumenti (TipoDocumento);

CREATE INDEX IX_T_SottofaseDocumenti_Attivo
ON T_SottofaseDocumenti (Attivo);

CREATE INDEX IX_T_SottofaseDocumenti_DataCollegamento
ON T_SottofaseDocumenti (DataCollegamento);

CREATE INDEX IX_T_SottofaseDocumenti_Versione
ON T_SottofaseDocumenti (IDSottofase, VersioneDocumento);
```

## 5. Nuova tabella T_SottofaseStepOperativi

La tabella `T_SottofaseStepOperativi` registra lo stato dei cinque step interni della sottofase.

Ogni sottofase documentale dovrebbe avere, almeno logicamente, i seguenti step:

| CodiceStep | Ordine |
| --- | --- |
| `REDIGI` | 10 |
| `REVISIONA` | 20 |
| `FIRMA` | 30 |
| `PROTOCOLLA` | 40 |
| `FINE` | 50 |

```sql
CREATE TABLE T_SottofaseStepOperativi (
    IDStepSottofase COUNTER CONSTRAINT PK_T_SottofaseStepOperativi PRIMARY KEY,
    IDSottofase LONG,
    CodiceStep TEXT(50),
    Ordine INTEGER,
    StatoStep TEXT(50),
    DataAvvio DATETIME,
    DataCompletamento DATETIME,
    NoteStep MEMO,
    UtenteAssegnato TEXT(100),
    UtenteCompletamento TEXT(100),
    IDDocumentoSottofase LONG,
    VersioneDocumento INTEGER,
    DataCreazione DATETIME,
    DataModifica DATETIME
);
```

### Campi T_SottofaseStepOperativi

| Campo | Tipo Access | Significato operativo |
| --- | --- | --- |
| `IDStepSottofase` | `COUNTER` | Chiave primaria tecnica dello step interno. |
| `IDSottofase` | `LONG` | Riferimento a `T_ProcedimentoSottofasi.IDSottofase`. |
| `CodiceStep` | `TEXT(50)` | Step documentale: `REDIGI`, `REVISIONA`, `FIRMA`, `PROTOCOLLA`, `FINE`. |
| `Ordine` | `INTEGER` | Posizione dello step nel ciclo interno. |
| `StatoStep` | `TEXT(50)` | Stato dello step: `NON_AVVIATO`, `IN_CORSO`, `COMPLETATO`, `BLOCCATO`. |
| `DataAvvio` | `DATETIME` | Data e ora avvio step. |
| `DataCompletamento` | `DATETIME` | Data e ora completamento step. |
| `NoteStep` | `MEMO` | Note operative specifiche dello step. |
| `UtenteAssegnato` | `TEXT(100)` | Utente o ruolo assegnato allo step. |
| `UtenteCompletamento` | `TEXT(100)` | Utente che ha completato lo step. |
| `IDDocumentoSottofase` | `LONG` | Documento collegato allo step, se pertinente. |
| `VersioneDocumento` | `INTEGER` | Versione documento associata allo step. |
| `DataCreazione` | `DATETIME` | Data creazione record. |
| `DataModifica` | `DATETIME` | Data ultima modifica record. |

### Valori ammessi CodiceStep

- `REDIGI`
- `REVISIONA`
- `FIRMA`
- `PROTOCOLLA`
- `FINE`

### Valori ammessi StatoStep

- `NON_AVVIATO`
- `IN_CORSO`
- `COMPLETATO`
- `BLOCCATO`

### Indici consigliati T_SottofaseStepOperativi

```sql
CREATE INDEX IX_T_SottofaseStepOperativi_IDSottofase
ON T_SottofaseStepOperativi (IDSottofase);

CREATE INDEX IX_T_SottofaseStepOperativi_Ordine
ON T_SottofaseStepOperativi (IDSottofase, Ordine);

CREATE INDEX IX_T_SottofaseStepOperativi_CodiceStep
ON T_SottofaseStepOperativi (CodiceStep);

CREATE INDEX IX_T_SottofaseStepOperativi_StatoStep
ON T_SottofaseStepOperativi (StatoStep);

CREATE INDEX IX_T_SottofaseStepOperativi_Documento
ON T_SottofaseStepOperativi (IDDocumentoSottofase);
```

## 6. Relazioni logiche

Relazioni consigliate:

```text
T_ProcedimentoSottofasi.IDSottofase
  -> T_SottofaseDocumenti.IDSottofase

T_ProcedimentoSottofasi.IDSottofase
  -> T_SottofaseStepOperativi.IDSottofase

T_SottofaseDocumenti.IDDocumentoSottofase
  -> T_ProcedimentoSottofasi.IDDocumentoCorrente

T_SottofaseDocumenti.IDDocumentoSottofase
  -> T_SottofaseStepOperativi.IDDocumentoSottofase
```

In Access MVP si consiglia di partire con relazioni logiche gestite dal backend, senza imporre subito vincoli referenziali rigidi, per ridurre il rischio operativo su database esistente.

In PostgreSQL sara opportuno introdurre foreign key reali, vincoli `CHECK`, indici parziali e transazioni.

## 7. Strategia Word Desktop

Il comportamento desiderato per il pulsante `Redigi` deve essere progettato con attenzione.

Flusso prudente MVP:

1. l'utente clicca `Redigi`;
2. il frontend invita a selezionare un file Word;
3. il backend registra il documento collegato alla sottofase;
4. il backend salva o memorizza il percorso del file secondo strategia controllata;
5. il frontend mostra un'icona documento nel dettaglio sottofase;
6. l'apertura del documento avviene tramite backend Windows controllato, se il contesto runtime lo consente.

### Apertura file

L'apertura diretta di file locali dal browser non deve essere considerata affidabile o sicura. In un ambiente Windows locale controllato il backend puo offrire un endpoint dedicato che usa logica server-side per aprire il documento, analogamente a quanto gia avviene per alcuni PDF.

In un contesto multiutente o web reale, la strategia corretta diventera:

- download/upload nuova versione;
- storage condiviso controllato;
- integrazione futura con SharePoint, WebDAV, OnlyOffice, Office Online o sistema documentale dedicato.

### Icona frontend

Il frontend non deve dedurre l'esistenza del file solo dal nome. Deve ricevere dal backend un dato esplicito, ad esempio:

```json
{
  "ha_documento_collegato": true,
  "documento_corrente": {
    "id_documento_sottofase": 12,
    "nome_file": "Bozza_risposta.docx",
    "estensione": ".docx",
    "tipo_documento": "WORD"
  }
}
```

## 8. Rischi tecnici

### Access multiutente

Access non e ideale per scritture concorrenti frequenti. L'aggiunta di documenti, step e storico aumenta il numero di operazioni di scrittura. Per questo motivo:

- usare query parametrizzate;
- tenere transazioni brevi quando possibile;
- evitare aggiornamenti multipli non necessari;
- loggare ogni errore in modo chiaro;
- pianificare PostgreSQL come target definitivo.

### Path locali

Percorsi locali come `C:\...` funzionano solo se backend e file system sono nello stesso contesto operativo. In multiutente possono diventare ambigui.

### Path UNC

Percorsi UNC come `\\server\share\...` sono piu adatti a contesti condivisi, ma richiedono permessi coerenti per l'utente/processo che esegue il backend.

### Sicurezza percorsi

Il backend deve normalizzare e validare i path:

- bloccare path traversal;
- evitare apertura di file fuori dalle radici autorizzate;
- distinguere path assoluti, UNC e relativi;
- verificare esistenza file prima di proporre apertura/download;
- non fidarsi di path ricevuti direttamente dal frontend.

### Migrazione PostgreSQL

Lo schema proposto e PostgreSQL-friendly perche:

- usa chiavi surrogate;
- separa sottofase, documenti e step;
- evita campi multipli ripetuti nella stessa tabella;
- mantiene relazioni normalizzate;
- prepara foreign key reali;
- consente storage documentale separato dal database.

### Versioning futuro

`VersioneDocumento` e presente sia sulla sottofase sia sul documento/step. La fonte autorevole dovrebbe essere `T_SottofaseDocumenti.VersioneDocumento`. Il campo su `T_ProcedimentoSottofasi` serve solo come cache operativa del documento corrente.

## 9. Rollback manuale

Se in futuro lo schema verra applicato realmente e sara necessario un rollback manuale, l'ordine prudente sara:

1. rimuovere eventuali relazioni Access manuali/grafiche;
2. eliminare indici sulle nuove tabelle;
3. eliminare `T_SottofaseStepOperativi`;
4. eliminare `T_SottofaseDocumenti`;
5. valutare se lasciare o rimuovere i campi aggiunti a `T_ProcedimentoSottofasi`.

Access non gestisce il DDL in modo transazionale come PostgreSQL. Prima di qualsiasi modifica reale e obbligatorio creare un backup con timestamp.

Esempio rollback concettuale:

```sql
DROP TABLE T_SottofaseStepOperativi;
DROP TABLE T_SottofaseDocumenti;
```

Per i campi aggiunti a `T_ProcedimentoSottofasi`, il rollback va valutato con estrema prudenza. Se sono gia stati popolati, rimuoverli comporta perdita dati. In Access e preferibile eseguire il rollback ripristinando il backup.

## 10. Checklist pre-esecuzione reale

Prima di applicare qualunque DDL reale al file `.accdb`:

- [ ] creare backup con data e ora nel nome file;
- [ ] verificare che il backup esista;
- [ ] verificare che il backup abbia dimensione maggiore di zero;
- [ ] verificare, se possibile, che la dimensione del backup coincida con il file sorgente;
- [ ] eseguire inizialmente lo script solo su una copia del database;
- [ ] verificare assenza di lock anomali `.laccdb`;
- [ ] verificare che il database non sia aperto in esclusiva;
- [ ] verificare eventuali sincronizzazioni OneDrive/Cloud;
- [ ] verificare antivirus o processi che possano bloccare il file;
- [ ] verificare che `T_ProcedimentoSottofasi` esista e sia conforme allo schema workflow attuale;
- [ ] verificare se i campi da aggiungere esistono gia;
- [ ] verificare se le tabelle nuove esistono gia;
- [ ] se una tabella esiste gia, controllare manualmente i campi prima di procedere;
- [ ] eseguire lo script in modo manuale e controllato;
- [ ] validare tabelle, campi e indici dopo l'esecuzione.

## 11. Prossimi passi consigliati

1. Preparare lo script Access operativo senza eseguirlo.
2. Revisionare tecnicamente lo script.
3. Applicare lo schema reale solo dopo backup verificato.
4. Creare repository/service read-only per documenti e step sottofase.
5. Esporre API read-only.
6. Aggiornare frontend per mostrare ciclo interno e icona documento.
7. Introdurre in seguito la prima scrittura controllata: collegamento documento Word.

## 12. Cosa non implementare subito

Non conviene introdurre subito:

- apertura automatica Word senza backend controllato;
- salvataggio automatico intercettato dal browser;
- firma digitale reale;
- protocollazione automatica;
- versioning documentale completo;
- storico audit avanzato;
- gestione multiutente completa;
- integrazione SharePoint/Office Online;
- vincoli referenziali rigidi Access prima di test su copia.

La sequenza prudente resta: schema documentato, script revisionato, applicazione con backup, lettura backend, UI read-only, poi scrittura minima e controllata.
