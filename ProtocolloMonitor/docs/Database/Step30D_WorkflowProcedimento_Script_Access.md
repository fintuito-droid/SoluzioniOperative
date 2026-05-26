# Step 30D - Script Access Workflow Procedimento

## 1. Premessa operativa

Questo documento contiene lo script VBA operativo per creare le tabelle MVP del workflow procedimento nel database Access di ProtocolloMonitor.

Lo script e pensato per essere copiato manualmente in un modulo VBA standard di Microsoft Access ed eseguito solo dopo verifica tecnica su una copia del database.

Questo documento non esegue alcuna modifica al database.

Tabelle previste:

- `T_ProcedimentoFasi`
- `T_ProcedimentoSottofasi`
- `L_CatalogoSottofasi`

Lo script inserisce inoltre nel catalogo sottofasi le voci iniziali usate dalla demo dello Step 30B:

- `VERIFICA_OGGETTO`
- `TELEFONATA`
- `EMAIL`
- `DOCUMENTO`
- `UFFICIO`
- `PRIORITA`
- `FIRMA`
- `CONTROLLO`

## 2. Regola obbligatoria di sicurezza

Prima di eseguire qualsiasi modifica reale al file `.accdb` deve essere creato un backup con data e ora nel nome file.

Formato consigliato:

```text
Backup\ProtocolloMonitor_BACKUP_YYYYMMDD_HHNNSS.accdb
```

Se il backup fallisce, lo script non deve proseguire.

Non procedere mai alla creazione di tabelle, indici o dati catalogo se:

- il percorso del database non e identificabile;
- la cartella `Backup` non puo essere creata;
- la copia del file `.accdb` non riesce;
- il file copiato non esiste dopo la copia;
- e presente un file `.laccdb`;
- il database e aperto in modalita esclusiva.

## 3. Note rischi prima dell'esecuzione

Rischi operativi da verificare prima dell'esecuzione reale:

- database sincronizzato con OneDrive o altri sistemi cloud che possono bloccare temporaneamente il file;
- presenza del file di lock `.laccdb`;
- antivirus o sistemi di protezione endpoint che intercettano la copia del file;
- database aperto in modalita esclusiva da Access o da un altro utente;
- DDL Access non transazionale come PostgreSQL: se lo script fallisce a meta, possono restare tabelle o indici gia creati.

## 4. Script VBA completo

> Copiare il codice seguente in un modulo VBA Access.
>
> Non viene eseguito automaticamente.
>
> Avviare manualmente la macro `CreaSchemaWorkflowProcedimento_MVP`.

```vba
Option Compare Database
Option Explicit

' =============================================================================
' ProtocolloMonitor - Creazione schema MVP Workflow Procedimento
' =============================================================================
'
' SCOPO
' -----
' Crea le tabelle Access:
' - T_ProcedimentoFasi
' - T_ProcedimentoSottofasi
' - L_CatalogoSottofasi
'
' Crea gli indici consigliati e inserisce le voci iniziali nel catalogo
' sottofasi senza duplicarle.
'
' SICUREZZA
' ---------
' Prima di modificare il database crea un backup del file .accdb corrente.
' Se il backup non riesce o non viene verificato, lo script si interrompe.
'
' NOTE
' ----
' Lo script e idempotente a livello operativo:
' - se una tabella esiste gia, non viene ricreata;
' - se un indice esiste gia, non viene ricreato;
' - se una voce catalogo esiste gia, non viene duplicata.
'
' =============================================================================

Public Sub CreaSchemaWorkflowProcedimento_MVP()
    On Error GoTo GestioneErrore

    Dim db As DAO.Database
    Dim percorsoDatabase As String
    Dim percorsoBackup As String

    Set db = CurrentDb
    percorsoDatabase = CurrentDb.Name

    If Len(Trim$(percorsoDatabase)) = 0 Then
        Err.Raise vbObjectError + 3000, , "Percorso database corrente non disponibile."
    End If

    VerificaAssenzaLock percorsoDatabase

    percorsoBackup = CreaBackupDatabaseCorrente(percorsoDatabase)

    If Len(Trim$(percorsoBackup)) = 0 Then
        Err.Raise vbObjectError + 3001, , "Backup non creato. Creazione schema interrotta."
    End If

    If Dir(percorsoBackup) = "" Then
        Err.Raise vbObjectError + 3002, , "Backup non verificabile. Creazione schema interrotta."
    End If

    CreaTabellaProcedimentoFasi db
    CreaTabellaProcedimentoSottofasi db
    CreaTabellaCatalogoSottofasi db

    CreaIndiciProcedimentoFasi db
    CreaIndiciProcedimentoSottofasi db
    CreaIndiciCatalogoSottofasi db

    InserisciCatalogoSottofasiIniziale db

    MsgBox _
        "Schema Workflow Procedimento creato/verificato correttamente." & vbCrLf & _
        "Backup creato in:" & vbCrLf & percorsoBackup, _
        vbInformation, _
        "ProtocolloMonitor"

    Exit Sub

GestioneErrore:
    MsgBox _
        "Errore durante la creazione schema Workflow Procedimento." & vbCrLf & _
        "Numero errore: " & Err.Number & vbCrLf & _
        "Descrizione: " & Err.Description, _
        vbCritical, _
        "ProtocolloMonitor"
End Sub


Private Sub VerificaAssenzaLock(ByVal percorsoDatabase As String)
    Dim fso As Object
    Dim cartellaDatabase As String
    Dim nomeSenzaEstensione As String
    Dim percorsoLock As String

    Set fso = CreateObject("Scripting.FileSystemObject")

    cartellaDatabase = fso.GetParentFolderName(percorsoDatabase)
    nomeSenzaEstensione = fso.GetBaseName(percorsoDatabase)
    percorsoLock = fso.BuildPath(cartellaDatabase, nomeSenzaEstensione & ".laccdb")

    If fso.FileExists(percorsoLock) Then
        Err.Raise vbObjectError + 3100, , "File lock Access presente: " & percorsoLock
    End If
End Sub


Private Function CreaBackupDatabaseCorrente(ByVal percorsoDatabase As String) As String
    On Error GoTo GestioneErrore

    Dim fso As Object
    Dim cartellaDatabase As String
    Dim nomeSenzaEstensione As String
    Dim estensione As String
    Dim cartellaBackup As String
    Dim percorsoBackup As String
    Dim timestamp As String

    Set fso = CreateObject("Scripting.FileSystemObject")

    cartellaDatabase = fso.GetParentFolderName(percorsoDatabase)
    nomeSenzaEstensione = fso.GetBaseName(percorsoDatabase)
    estensione = fso.GetExtensionName(percorsoDatabase)

    If Len(Trim$(cartellaDatabase)) = 0 Then
        Err.Raise vbObjectError + 3200, , "Cartella database non identificabile."
    End If

    If Len(Trim$(nomeSenzaEstensione)) = 0 Then
        Err.Raise vbObjectError + 3201, , "Nome database non identificabile."
    End If

    cartellaBackup = fso.BuildPath(cartellaDatabase, "Backup")

    If Not fso.FolderExists(cartellaBackup) Then
        fso.CreateFolder cartellaBackup
    End If

    timestamp = Format(Now, "yyyymmdd_hhnnss")
    percorsoBackup = fso.BuildPath(cartellaBackup, nomeSenzaEstensione & "_BACKUP_" & timestamp & "." & estensione)

    fso.CopyFile percorsoDatabase, percorsoBackup, False

    If Not fso.FileExists(percorsoBackup) Then
        Err.Raise vbObjectError + 3202, , "Il file backup non esiste dopo la copia."
    End If

    CreaBackupDatabaseCorrente = percorsoBackup
    Exit Function

GestioneErrore:
    CreaBackupDatabaseCorrente = ""
    Err.Raise Err.Number, , "Backup fallito: " & Err.Description
End Function


Private Sub CreaTabellaProcedimentoFasi(ByVal db As DAO.Database)
    If TabellaEsiste(db, "T_ProcedimentoFasi") Then
        Exit Sub
    End If

    db.Execute _
        "CREATE TABLE T_ProcedimentoFasi (" & _
        "IDFase AUTOINCREMENT CONSTRAINT PK_T_ProcedimentoFasi PRIMARY KEY, " & _
        "IDProcedimento LONG, " & _
        "CodiceFase TEXT(50), " & _
        "Titolo TEXT(255), " & _
        "Descrizione LONGTEXT, " & _
        "Ordine INTEGER, " & _
        "StatoFase TEXT(50), " & _
        "Responsabile TEXT(255), " & _
        "DataScadenza DATETIME, " & _
        "DataAvvio DATETIME, " & _
        "DataCompletamento DATETIME, " & _
        "Obbligatoria YESNO, " & _
        "Bloccante YESNO, " & _
        "Attivo YESNO, " & _
        "DataCreazione DATETIME, " & _
        "DataModifica DATETIME" & _
        ")", _
        dbFailOnError
End Sub


Private Sub CreaTabellaProcedimentoSottofasi(ByVal db As DAO.Database)
    If TabellaEsiste(db, "T_ProcedimentoSottofasi") Then
        Exit Sub
    End If

    db.Execute _
        "CREATE TABLE T_ProcedimentoSottofasi (" & _
        "IDSottofase AUTOINCREMENT CONSTRAINT PK_T_ProcedimentoSottofasi PRIMARY KEY, " & _
        "IDFase LONG, " & _
        "IDCatalogoSottofase LONG, " & _
        "CodiceSottofase TEXT(50), " & _
        "Titolo TEXT(255), " & _
        "Descrizione LONGTEXT, " & _
        "Ordine INTEGER, " & _
        "StatoSottofase TEXT(50), " & _
        "Icona TEXT(100), " & _
        "Colore TEXT(50), " & _
        "Responsabile TEXT(255), " & _
        "DataScadenza DATETIME, " & _
        "DataAvvio DATETIME, " & _
        "DataCompletamento DATETIME, " & _
        "NoteInterne LONGTEXT, " & _
        "Attivo YESNO, " & _
        "DataCreazione DATETIME, " & _
        "DataModifica DATETIME" & _
        ")", _
        dbFailOnError
End Sub


Private Sub CreaTabellaCatalogoSottofasi(ByVal db As DAO.Database)
    If TabellaEsiste(db, "L_CatalogoSottofasi") Then
        Exit Sub
    End If

    db.Execute _
        "CREATE TABLE L_CatalogoSottofasi (" & _
        "IDCatalogoSottofase AUTOINCREMENT CONSTRAINT PK_L_CatalogoSottofasi PRIMARY KEY, " & _
        "CodiceSottofase TEXT(50), " & _
        "Titolo TEXT(255), " & _
        "Descrizione LONGTEXT, " & _
        "Icona TEXT(100), " & _
        "Colore TEXT(50), " & _
        "Categoria TEXT(100), " & _
        "OrdineDefault INTEGER, " & _
        "Attivo YESNO, " & _
        "DataCreazione DATETIME, " & _
        "DataModifica DATETIME" & _
        ")", _
        dbFailOnError
End Sub


Private Sub CreaIndiciProcedimentoFasi(ByVal db As DAO.Database)
    CreaIndiceSeAssente db, "T_ProcedimentoFasi", "IX_T_ProcedimentoFasi_IDProcedimento", "IDProcedimento", False
    CreaIndiceSeAssente db, "T_ProcedimentoFasi", "IX_T_ProcedimentoFasi_StatoFase", "StatoFase", False
    CreaIndiceSeAssente db, "T_ProcedimentoFasi", "IX_T_ProcedimentoFasi_Ordine", "IDProcedimento, Ordine", False
    CreaIndiceSeAssente db, "T_ProcedimentoFasi", "IX_T_ProcedimentoFasi_DataScadenza", "DataScadenza", False
End Sub


Private Sub CreaIndiciProcedimentoSottofasi(ByVal db As DAO.Database)
    CreaIndiceSeAssente db, "T_ProcedimentoSottofasi", "IX_T_ProcedimentoSottofasi_IDFase", "IDFase", False
    CreaIndiceSeAssente db, "T_ProcedimentoSottofasi", "IX_T_ProcedimentoSottofasi_StatoSottofase", "StatoSottofase", False
    CreaIndiceSeAssente db, "T_ProcedimentoSottofasi", "IX_T_ProcedimentoSottofasi_Ordine", "IDFase, Ordine", False
    CreaIndiceSeAssente db, "T_ProcedimentoSottofasi", "IX_T_ProcedimentoSottofasi_IDCatalogoSottofase", "IDCatalogoSottofase", False
End Sub


Private Sub CreaIndiciCatalogoSottofasi(ByVal db As DAO.Database)
    CreaIndiceSeAssente db, "L_CatalogoSottofasi", "UX_L_CatalogoSottofasi_CodiceSottofase", "CodiceSottofase", True
    CreaIndiceSeAssente db, "L_CatalogoSottofasi", "IX_L_CatalogoSottofasi_Attivo", "Attivo", False
End Sub


Private Sub InserisciCatalogoSottofasiIniziale(ByVal db As DAO.Database)
    InserisciCatalogoSottofaseSeAssente db, "VERIFICA_OGGETTO", "Verifica oggetto", "Controllo del testo dell'oggetto della nota.", "mdi-text-search", "blue", "OPERATIVA", 10
    InserisciCatalogoSottofaseSeAssente db, "TELEFONATA", "Telefonata", "Contatto telefonico con ufficio, Comando o referente.", "mdi-phone", "green", "COMUNICAZIONE", 20
    InserisciCatalogoSottofaseSeAssente db, "EMAIL", "Email", "Invio o verifica di una comunicazione tramite posta elettronica.", "mdi-email-outline", "indigo", "COMUNICAZIONE", 30
    InserisciCatalogoSottofaseSeAssente db, "DOCUMENTO", "Documento", "Predisposizione o verifica di un documento amministrativo.", "mdi-file-document-outline", "deep-purple", "DOCUMENTALE", 40
    InserisciCatalogoSottofaseSeAssente db, "UFFICIO", "Ufficio competente", "Individuazione dell'ufficio responsabile della lavorazione.", "mdi-office-building", "cyan", "ORGANIZZATIVA", 50
    InserisciCatalogoSottofaseSeAssente db, "PRIORITA", "Priorita", "Attribuzione della priorita operativa o amministrativa.", "mdi-alert-circle-outline", "orange", "OPERATIVA", 60
    InserisciCatalogoSottofaseSeAssente db, "FIRMA", "Firma", "Acquisizione o verifica della firma del responsabile.", "mdi-draw-pen", "brown", "DOCUMENTALE", 70
    InserisciCatalogoSottofaseSeAssente db, "CONTROLLO", "Controllo finale", "Verifica conclusiva prima della chiusura della fase.", "mdi-check-decagram", "teal", "CONTROLLO", 80
End Sub


Private Sub InserisciCatalogoSottofaseSeAssente( _
    ByVal db As DAO.Database, _
    ByVal codice As String, _
    ByVal titolo As String, _
    ByVal descrizione As String, _
    ByVal icona As String, _
    ByVal colore As String, _
    ByVal categoria As String, _
    ByVal ordineDefault As Integer)

    If CatalogoSottofaseEsiste(db, codice) Then
        Exit Sub
    End If

    Dim sql As String

    sql = "INSERT INTO L_CatalogoSottofasi (" & _
          "CodiceSottofase, Titolo, Descrizione, Icona, Colore, Categoria, OrdineDefault, Attivo, DataCreazione, DataModifica" & _
          ") VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"

    Dim query As DAO.QueryDef
    Set query = db.CreateQueryDef("", sql)

    query.Parameters(0).Value = codice
    query.Parameters(1).Value = titolo
    query.Parameters(2).Value = descrizione
    query.Parameters(3).Value = icona
    query.Parameters(4).Value = colore
    query.Parameters(5).Value = categoria
    query.Parameters(6).Value = ordineDefault
    query.Parameters(7).Value = True
    query.Parameters(8).Value = Now
    query.Parameters(9).Value = Now

    query.Execute dbFailOnError
    query.Close
    Set query = Nothing
End Sub


Private Function CatalogoSottofaseEsiste(ByVal db As DAO.Database, ByVal codice As String) As Boolean
    On Error GoTo GestioneErrore

    Dim query As DAO.QueryDef
    Dim rs As DAO.Recordset

    Set query = db.CreateQueryDef("", "SELECT COUNT(*) AS Totale FROM L_CatalogoSottofasi WHERE CodiceSottofase = ?")
    query.Parameters(0).Value = codice
    Set rs = query.OpenRecordset(dbOpenSnapshot)

    CatalogoSottofaseEsiste = (rs!Totale > 0)

    rs.Close
    query.Close
    Set rs = Nothing
    Set query = Nothing
    Exit Function

GestioneErrore:
    CatalogoSottofaseEsiste = False
End Function


Private Sub CreaIndiceSeAssente( _
    ByVal db As DAO.Database, _
    ByVal nomeTabella As String, _
    ByVal nomeIndice As String, _
    ByVal campiIndice As String, _
    ByVal univoco As Boolean)

    Dim sql As String

    If Not TabellaEsiste(db, nomeTabella) Then
        Err.Raise vbObjectError + 3300, , "Tabella non trovata per indice: " & nomeTabella
    End If

    If IndiceEsiste(db, nomeTabella, nomeIndice) Then
        Exit Sub
    End If

    If univoco Then
        sql = "CREATE UNIQUE INDEX " & nomeIndice & " ON " & nomeTabella & " (" & campiIndice & ")"
    Else
        sql = "CREATE INDEX " & nomeIndice & " ON " & nomeTabella & " (" & campiIndice & ")"
    End If

    db.Execute sql, dbFailOnError
End Sub


Private Function TabellaEsiste(ByVal db As DAO.Database, ByVal nomeTabella As String) As Boolean
    On Error GoTo NonEsiste

    Dim tdf As DAO.TableDef
    Set tdf = db.TableDefs(nomeTabella)

    TabellaEsiste = True
    Exit Function

NonEsiste:
    TabellaEsiste = False
End Function


Private Function IndiceEsiste( _
    ByVal db As DAO.Database, _
    ByVal nomeTabella As String, _
    ByVal nomeIndice As String) As Boolean

    On Error GoTo NonEsiste

    Dim idx As DAO.Index
    Set idx = db.TableDefs(nomeTabella).Indexes(nomeIndice)

    IndiceEsiste = True
    Exit Function

NonEsiste:
    IndiceEsiste = False
End Function
```

## 5. Controlli anti-duplicazione

Lo script contiene controlli per evitare duplicazioni operative:

- `TabellaEsiste(...)`: se una tabella esiste gia, non viene ricreata;
- `IndiceEsiste(...)`: se un indice esiste gia, non viene ricreato;
- `CatalogoSottofaseEsiste(...)`: se una voce catalogo esiste gia, non viene reinserita.

Nota importante: se una tabella esiste gia ma con struttura diversa, lo script non la modifica. In quel caso serve analisi manuale prima di procedere.

## 6. Lo script non deve essere eseguito automaticamente

Questo script non deve essere collegato a:

- macro automatiche;
- apertura database;
- pulsanti di produzione;
- avvio di FastAPI;
- avvio di Flask;
- flusso Grisù.

Deve essere eseguito manualmente da un operatore consapevole, dopo backup e verifica su copia del database.

## 7. Uso previsto in Access

Procedura consigliata:

1. aprire una copia del database Access;
2. aprire l'editor VBA;
3. creare un nuovo modulo standard;
4. copiare lo script completo;
5. verificare che il riferimento DAO sia disponibile;
6. eseguire manualmente `CreaSchemaWorkflowProcedimento_MVP`;
7. controllare tabelle, indici e righe catalogo.

Compatibilita DAO VBA:

- lo script usa `DAO.Database`, `DAO.TableDef`, `DAO.Index`, `DAO.QueryDef` e `DAO.Recordset`;
- in Access deve essere disponibile il riferimento DAO/Access Database Engine Object Library;
- se l'editor VBA segnala errore sui tipi `DAO.*`, verificare i riferimenti del progetto VBA prima di eseguire lo script.

## 8. Rollback manuale

Rollback preferito:

1. chiudere Access;
2. ripristinare il file `.accdb` dal backup creato dallo script;
3. riaprire il database ripristinato;
4. verificare che `T_Procedimenti` e `T_ProcedimentoProtocolli` siano ancora presenti;
5. verificare che le nuove tabelle workflow non siano presenti se si e tornati al backup precedente.

Rollback SQL manuale, solo se non ci sono dati workflow da conservare:

```sql
DROP TABLE T_ProcedimentoSottofasi;
DROP TABLE T_ProcedimentoFasi;
DROP TABLE L_CatalogoSottofasi;
```

Ordine importante:

1. eliminare prima `T_ProcedimentoSottofasi`;
2. eliminare poi `T_ProcedimentoFasi`;
3. eliminare infine `L_CatalogoSottofasi`.

Se sono state create relazioni Access manuali, rimuoverle prima del `DROP TABLE`.

## 9. Checklist post-esecuzione

Dopo l'esecuzione reale, verificare:

- [ ] La cartella `Backup` esiste accanto al file `.accdb`.
- [ ] Il backup con timestamp e stato creato.
- [ ] Il backup e apribile o copiabile.
- [ ] `T_ProcedimentoFasi` esiste.
- [ ] `T_ProcedimentoSottofasi` esiste.
- [ ] `L_CatalogoSottofasi` esiste.
- [ ] `IDFase` e chiave primaria.
- [ ] `IDSottofase` e chiave primaria.
- [ ] `IDCatalogoSottofase` e chiave primaria.
- [ ] Gli indici `IX_T_ProcedimentoFasi_*` sono presenti.
- [ ] Gli indici `IX_T_ProcedimentoSottofasi_*` sono presenti.
- [ ] L'indice `UX_L_CatalogoSottofasi_CodiceSottofase` e presente.
- [ ] Le 8 voci catalogo iniziali sono presenti una sola volta.
- [ ] `T_Procedimenti` non e stata modificata.
- [ ] `T_ProcedimentoProtocolli` non e stata modificata.
- [ ] Gli endpoint FastAPI esistenti continuano a funzionare.
- [ ] Il frontend continua a visualizzare procedimento e protocolli collegati.
- [ ] Il flusso Flask/Grisù continua ad acquisire protocolli.
