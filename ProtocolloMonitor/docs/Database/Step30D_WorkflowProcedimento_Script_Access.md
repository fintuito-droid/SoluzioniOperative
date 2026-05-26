# Step 30D - Script Access Workflow Procedimento

## 1. Premessa operativa

Questo documento contiene lo script VBA operativo per creare le tabelle MVP del workflow procedimento nel database Access di ProtocolloMonitor.

Lo script e pensato per essere copiato manualmente in un modulo VBA standard di Microsoft Access ed eseguito solo dopo verifica tecnica su una copia locale del database, preferibilmente non sincronizzata con OneDrive o altri sistemi cloud.

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

## 2. Modalita operative supportate

Lo script distingue due scenari.

### A. Esecuzione dentro una copia Access aperta

Questa e la modalita piu semplice per una prima prova manuale.

In questo caso il file `.laccdb` accanto al database puo essere normale, perche viene creato dalla sessione Access corrente. Lo script quindi non blocca automaticamente l'esecuzione solo perche esiste il lock del database corrente.

Resta obbligatorio:

- lavorare prima su una copia del database;
- creare e verificare il backup prima di qualsiasi DDL;
- interrompere se la copia backup fallisce;
- non usare questa modalita sul database runtime senza test precedente.

### B. Esecuzione da database utility verso database target chiuso

Questa e la modalita piu prudente per una futura applicazione reale.

Si crea un piccolo database Access di utilita, si copia lo script in quel database, si imposta il percorso del database target e si lascia chiuso il database target.

In questa modalita la presenza del file `.laccdb` del database target e un segnale di rischio e lo script si deve fermare.

## 3. Regola obbligatoria di sicurezza

Prima di eseguire qualsiasi modifica reale al file `.accdb` deve essere creato un backup con data e ora nel nome file.

Formato consigliato:

```text
Backup\ProtocolloMonitor_BACKUP_YYYYMMDD_HHNNSS.accdb
```

Se il backup fallisce, lo script non deve proseguire.

La verifica backup deve controllare:

- il file backup esiste;
- la dimensione del backup e maggiore di zero;
- se verificabile, la dimensione del backup coincide con la dimensione del file sorgente.

Consiglio operativo: prima di ogni esecuzione reale, provare lo script su una copia locale non sincronizzata del database.

## 4. Note rischi prima dell'esecuzione

Rischi operativi da verificare prima dell'esecuzione reale:

- database sincronizzato con OneDrive o altri sistemi cloud che possono bloccare temporaneamente il file;
- presenza del file di lock `.laccdb` non riconducibile alla sessione Access corrente;
- antivirus o sistemi di protezione endpoint che intercettano la copia del file;
- database aperto in modalita esclusiva da Access o da un altro utente;
- backup del database aperto: se la copia file fallisce o la dimensione non torna, lo script deve interrompersi;
- DDL Access non transazionale come PostgreSQL: se lo script fallisce a meta, possono restare tabelle o indici gia creati.

## 5. Script VBA completo

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
' MODALITA OPERATIVE
' ------------------
' A) USA_DATABASE_TARGET_ESTERNO = False
'    Lo script lavora sul database Access corrente. In questo scenario un file
'    .laccdb puo essere normale, perche generato dalla sessione corrente.
'
' B) USA_DATABASE_TARGET_ESTERNO = True
'    Lo script lavora su un database target chiuso, indicato da
'    PERCORSO_DATABASE_TARGET. In questo scenario la presenza del file .laccdb
'    del target blocca l'esecuzione.
'
' SICUREZZA
' ---------
' Prima di modificare il database crea un backup del file .accdb target.
' Se il backup non riesce o non viene verificato, lo script si interrompe.
'
' NOTE
' ----
' Lo script e idempotente a livello operativo:
' - se una tabella esiste gia, non viene ricreata;
' - se un indice esiste gia, non viene ricreato;
' - se una voce catalogo esiste gia, non viene duplicata.
'
' Se una tabella esiste ma ha struttura non conforme, lo script non prova a
' correggerla automaticamente: segnala errore sui campi mancanti.
'
' =============================================================================

Private Const USA_DATABASE_TARGET_ESTERNO As Boolean = False
Private Const PERCORSO_DATABASE_TARGET As String = ""

Public Sub CreaSchemaWorkflowProcedimento_MVP()
    On Error GoTo GestioneErrore

    Dim db As DAO.Database
    Dim percorsoDatabase As String
    Dim percorsoBackup As String
    Dim databaseEsternoAperto As Boolean
    Dim lockConsentitoSessioneCorrente As Boolean

    databaseEsternoAperto = False

    If USA_DATABASE_TARGET_ESTERNO Then
        percorsoDatabase = Trim$(PERCORSO_DATABASE_TARGET)
        lockConsentitoSessioneCorrente = False

        If Len(percorsoDatabase) = 0 Then
            Err.Raise vbObjectError + 3000, , "PERCORSO_DATABASE_TARGET non configurato."
        End If

        If Dir(percorsoDatabase) = "" Then
            Err.Raise vbObjectError + 3001, , "Database target non trovato: " & percorsoDatabase
        End If
    Else
        Set db = CurrentDb
        percorsoDatabase = CurrentDb.Name
        lockConsentitoSessioneCorrente = True

        If Len(Trim$(percorsoDatabase)) = 0 Then
            Err.Raise vbObjectError + 3002, , "Percorso database corrente non disponibile."
        End If
    End If

    VerificaLockDatabase percorsoDatabase, lockConsentitoSessioneCorrente

    percorsoBackup = CreaBackupDatabaseCorrente(percorsoDatabase)
    VerificaBackupDatabase percorsoDatabase, percorsoBackup

    If USA_DATABASE_TARGET_ESTERNO Then
        Set db = DBEngine.Workspaces(0).OpenDatabase(percorsoDatabase)
        databaseEsternoAperto = True
    End If

    CreaTabellaProcedimentoFasi db
    CreaTabellaProcedimentoSottofasi db
    CreaTabellaCatalogoSottofasi db

    VerificaStrutturaWorkflow db

    CreaIndiciProcedimentoFasi db
    CreaIndiciProcedimentoSottofasi db
    CreaIndiciCatalogoSottofasi db

    InserisciCatalogoSottofasiIniziale db

    If databaseEsternoAperto Then
        db.Close
        databaseEsternoAperto = False
    End If

    MsgBox _
        "Schema Workflow Procedimento creato/verificato correttamente." & vbCrLf & _
        "Backup creato in:" & vbCrLf & percorsoBackup, _
        vbInformation, _
        "ProtocolloMonitor"

    Exit Sub

GestioneErrore:
    On Error Resume Next
    If databaseEsternoAperto Then
        db.Close
    End If
    On Error GoTo 0

    MsgBox _
        "Errore durante la creazione schema Workflow Procedimento." & vbCrLf & _
        "Numero errore: " & Err.Number & vbCrLf & _
        "Descrizione: " & Err.Description, _
        vbCritical, _
        "ProtocolloMonitor"
End Sub


Private Sub VerificaLockDatabase(ByVal percorsoDatabase As String, ByVal lockConsentitoSessioneCorrente As Boolean)
    Dim fso As Object
    Dim cartellaDatabase As String
    Dim nomeSenzaEstensione As String
    Dim percorsoLock As String

    Set fso = CreateObject("Scripting.FileSystemObject")

    cartellaDatabase = fso.GetParentFolderName(percorsoDatabase)
    nomeSenzaEstensione = fso.GetBaseName(percorsoDatabase)
    percorsoLock = fso.BuildPath(cartellaDatabase, nomeSenzaEstensione & ".laccdb")

    If fso.FileExists(percorsoLock) Then
        If lockConsentitoSessioneCorrente Then
            Exit Sub
        End If

        Err.Raise vbObjectError + 3100, , "File lock Access presente sul database target chiuso: " & percorsoLock
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

    CreaBackupDatabaseCorrente = percorsoBackup
    Exit Function

GestioneErrore:
    CreaBackupDatabaseCorrente = ""
    Err.Raise Err.Number, , "Backup fallito: " & Err.Description
End Function


Private Sub VerificaBackupDatabase(ByVal percorsoDatabase As String, ByVal percorsoBackup As String)
    Dim fso As Object
    Dim dimensioneOrigine As Currency
    Dim dimensioneBackup As Currency

    Set fso = CreateObject("Scripting.FileSystemObject")

    If Len(Trim$(percorsoBackup)) = 0 Then
        Err.Raise vbObjectError + 3210, , "Backup non creato. Creazione schema interrotta."
    End If

    If Not fso.FileExists(percorsoBackup) Then
        Err.Raise vbObjectError + 3211, , "Il file backup non esiste dopo la copia."
    End If

    dimensioneBackup = fso.GetFile(percorsoBackup).Size

    If dimensioneBackup <= 0 Then
        Err.Raise vbObjectError + 3212, , "Il file backup ha dimensione zero."
    End If

    If fso.FileExists(percorsoDatabase) Then
        dimensioneOrigine = fso.GetFile(percorsoDatabase).Size

        If dimensioneOrigine > 0 Then
            If dimensioneBackup <> dimensioneOrigine Then
                Err.Raise vbObjectError + 3213, , _
                    "Dimensione backup diversa dal file sorgente. Backup non considerato sicuro."
            End If
        End If
    End If
End Sub


Private Sub CreaTabellaProcedimentoFasi(ByVal db As DAO.Database)
    If TabellaEsiste(db, "T_ProcedimentoFasi") Then
        Exit Sub
    End If

    db.Execute _
        "CREATE TABLE [T_ProcedimentoFasi] (" & _
        "[IDFase] COUNTER CONSTRAINT [PK_T_ProcedimentoFasi] PRIMARY KEY, " & _
        "[IDProcedimento] LONG, " & _
        "[CodiceFase] TEXT(50), " & _
        "[Titolo] TEXT(255), " & _
        "[Descrizione] MEMO, " & _
        "[Ordine] INTEGER, " & _
        "[StatoFase] TEXT(50), " & _
        "[Responsabile] TEXT(255), " & _
        "[DataScadenza] DATETIME, " & _
        "[DataAvvio] DATETIME, " & _
        "[DataCompletamento] DATETIME, " & _
        "[Obbligatoria] YESNO, " & _
        "[Bloccante] YESNO, " & _
        "[Attivo] YESNO, " & _
        "[DataCreazione] DATETIME, " & _
        "[DataModifica] DATETIME" & _
        ")", _
        dbFailOnError
End Sub


Private Sub CreaTabellaProcedimentoSottofasi(ByVal db As DAO.Database)
    If TabellaEsiste(db, "T_ProcedimentoSottofasi") Then
        Exit Sub
    End If

    db.Execute _
        "CREATE TABLE [T_ProcedimentoSottofasi] (" & _
        "[IDSottofase] COUNTER CONSTRAINT [PK_T_ProcedimentoSottofasi] PRIMARY KEY, " & _
        "[IDFase] LONG, " & _
        "[IDCatalogoSottofase] LONG, " & _
        "[CodiceSottofase] TEXT(50), " & _
        "[Titolo] TEXT(255), " & _
        "[Descrizione] MEMO, " & _
        "[Ordine] INTEGER, " & _
        "[StatoSottofase] TEXT(50), " & _
        "[Icona] TEXT(100), " & _
        "[Colore] TEXT(50), " & _
        "[Responsabile] TEXT(255), " & _
        "[DataScadenza] DATETIME, " & _
        "[DataAvvio] DATETIME, " & _
        "[DataCompletamento] DATETIME, " & _
        "[NoteInterne] MEMO, " & _
        "[Attivo] YESNO, " & _
        "[DataCreazione] DATETIME, " & _
        "[DataModifica] DATETIME" & _
        ")", _
        dbFailOnError
End Sub


Private Sub CreaTabellaCatalogoSottofasi(ByVal db As DAO.Database)
    If TabellaEsiste(db, "L_CatalogoSottofasi") Then
        Exit Sub
    End If

    db.Execute _
        "CREATE TABLE [L_CatalogoSottofasi] (" & _
        "[IDCatalogoSottofase] COUNTER CONSTRAINT [PK_L_CatalogoSottofasi] PRIMARY KEY, " & _
        "[CodiceSottofase] TEXT(50), " & _
        "[Titolo] TEXT(255), " & _
        "[Descrizione] MEMO, " & _
        "[Icona] TEXT(100), " & _
        "[Colore] TEXT(50), " & _
        "[Categoria] TEXT(100), " & _
        "[OrdineDefault] INTEGER, " & _
        "[Attivo] YESNO, " & _
        "[DataCreazione] DATETIME, " & _
        "[DataModifica] DATETIME" & _
        ")", _
        dbFailOnError
End Sub


Private Sub VerificaStrutturaWorkflow(ByVal db As DAO.Database)
    VerificaCampiRichiesti db, "T_ProcedimentoFasi", Array( _
        "IDFase", "IDProcedimento", "CodiceFase", "Titolo", "Descrizione", _
        "Ordine", "StatoFase", "Responsabile", "DataScadenza", "DataAvvio", _
        "DataCompletamento", "Obbligatoria", "Bloccante", "Attivo", _
        "DataCreazione", "DataModifica")

    VerificaCampiRichiesti db, "T_ProcedimentoSottofasi", Array( _
        "IDSottofase", "IDFase", "IDCatalogoSottofase", "CodiceSottofase", _
        "Titolo", "Descrizione", "Ordine", "StatoSottofase", "Icona", _
        "Colore", "Responsabile", "DataScadenza", "DataAvvio", _
        "DataCompletamento", "NoteInterne", "Attivo", "DataCreazione", _
        "DataModifica")

    VerificaCampiRichiesti db, "L_CatalogoSottofasi", Array( _
        "IDCatalogoSottofase", "CodiceSottofase", "Titolo", "Descrizione", _
        "Icona", "Colore", "Categoria", "OrdineDefault", "Attivo", _
        "DataCreazione", "DataModifica")
End Sub


Private Sub CreaIndiciProcedimentoFasi(ByVal db As DAO.Database)
    CreaIndiceSeAssente db, "T_ProcedimentoFasi", "IX_T_ProcedimentoFasi_IDProcedimento", False, "IDProcedimento"
    CreaIndiceSeAssente db, "T_ProcedimentoFasi", "IX_T_ProcedimentoFasi_StatoFase", False, "StatoFase"
    CreaIndiceSeAssente db, "T_ProcedimentoFasi", "IX_T_ProcedimentoFasi_Ordine", False, "IDProcedimento", "Ordine"
    CreaIndiceSeAssente db, "T_ProcedimentoFasi", "IX_T_ProcedimentoFasi_DataScadenza", False, "DataScadenza"
End Sub


Private Sub CreaIndiciProcedimentoSottofasi(ByVal db As DAO.Database)
    CreaIndiceSeAssente db, "T_ProcedimentoSottofasi", "IX_T_ProcedimentoSottofasi_IDFase", False, "IDFase"
    CreaIndiceSeAssente db, "T_ProcedimentoSottofasi", "IX_T_ProcedimentoSottofasi_StatoSottofase", False, "StatoSottofase"
    CreaIndiceSeAssente db, "T_ProcedimentoSottofasi", "IX_T_ProcedimentoSottofasi_Ordine", False, "IDFase", "Ordine"
    CreaIndiceSeAssente db, "T_ProcedimentoSottofasi", "IX_T_ProcedimentoSottofasi_IDCatalogoSottofase", False, "IDCatalogoSottofase"
End Sub


Private Sub CreaIndiciCatalogoSottofasi(ByVal db As DAO.Database)
    CreaIndiceSeAssente db, "L_CatalogoSottofasi", "UX_L_CatalogoSottofasi_CodiceSottofase", True, "CodiceSottofase"
    CreaIndiceSeAssente db, "L_CatalogoSottofasi", "IX_L_CatalogoSottofasi_Attivo", False, "Attivo"
End Sub


Private Sub InserisciCatalogoSottofasiIniziale(ByVal db As DAO.Database)
    VerificaCampiRichiesti db, "L_CatalogoSottofasi", Array( _
        "CodiceSottofase", "Titolo", "Descrizione", "Icona", "Colore", _
        "Categoria", "OrdineDefault", "Attivo", "DataCreazione", "DataModifica")

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

    Dim rs As DAO.Recordset

    If CatalogoSottofaseEsiste(db, codice) Then
        Exit Sub
    End If

    Set rs = db.OpenRecordset("L_CatalogoSottofasi", dbOpenDynaset)

    rs.AddNew
    rs![CodiceSottofase] = codice
    rs![Titolo] = titolo
    rs![Descrizione] = descrizione
    rs![Icona] = icona
    rs![Colore] = colore
    rs![Categoria] = categoria
    rs![OrdineDefault] = ordineDefault
    rs![Attivo] = True
    rs![DataCreazione] = Now
    rs![DataModifica] = Now
    rs.Update

    rs.Close
    Set rs = Nothing
End Sub


Private Function CatalogoSottofaseEsiste(ByVal db As DAO.Database, ByVal codice As String) As Boolean
    On Error GoTo GestioneErrore

    Dim query As DAO.QueryDef
    Dim rs As DAO.Recordset
    Dim sql As String

    sql = _
        "PARAMETERS pCodice TEXT(50); " & _
        "SELECT COUNT(*) AS Totale " & _
        "FROM [L_CatalogoSottofasi] " & _
        "WHERE [CodiceSottofase] = [pCodice]"

    Set query = db.CreateQueryDef("", sql)
    query.Parameters("pCodice").Value = codice
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
    ByVal univoco As Boolean, _
    ParamArray campi() As Variant)

    Dim sql As String
    Dim campiSql As String
    Dim i As Long

    If Not TabellaEsiste(db, nomeTabella) Then
        Err.Raise vbObjectError + 3300, , "Tabella non trovata per indice: " & nomeTabella
    End If

    For i = LBound(campi) To UBound(campi)
        If Not CampoEsiste(db, nomeTabella, CStr(campi(i))) Then
            Err.Raise vbObjectError + 3301, , _
                "Campo mancante per indice " & nomeIndice & ": " & nomeTabella & "." & CStr(campi(i))
        End If

        If Len(campiSql) > 0 Then
            campiSql = campiSql & ", "
        End If

        campiSql = campiSql & "[" & CStr(campi(i)) & "]"
    Next i

    If IndiceEsiste(db, nomeTabella, nomeIndice) Then
        Exit Sub
    End If

    If univoco Then
        sql = "CREATE UNIQUE INDEX [" & nomeIndice & "] ON [" & nomeTabella & "] (" & campiSql & ")"
    Else
        sql = "CREATE INDEX [" & nomeIndice & "] ON [" & nomeTabella & "] (" & campiSql & ")"
    End If

    db.Execute sql, dbFailOnError
End Sub


Private Sub VerificaCampiRichiesti(ByVal db As DAO.Database, ByVal nomeTabella As String, ByVal campiRichiesti As Variant)
    Dim i As Long

    If Not TabellaEsiste(db, nomeTabella) Then
        Err.Raise vbObjectError + 3400, , "Tabella obbligatoria mancante: " & nomeTabella
    End If

    For i = LBound(campiRichiesti) To UBound(campiRichiesti)
        If Not CampoEsiste(db, nomeTabella, CStr(campiRichiesti(i))) Then
            Err.Raise vbObjectError + 3401, , _
                "Tabella esistente ma non conforme. Campo mancante: " & nomeTabella & "." & CStr(campiRichiesti(i))
        End If
    Next i
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


Private Function CampoEsiste(ByVal db As DAO.Database, ByVal nomeTabella As String, ByVal nomeCampo As String) As Boolean
    On Error GoTo NonEsiste

    Dim fld As DAO.Field
    Set fld = db.TableDefs(nomeTabella).Fields(nomeCampo)

    CampoEsiste = True
    Exit Function

NonEsiste:
    CampoEsiste = False
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

## 6. Controlli anti-duplicazione

Lo script contiene controlli per evitare duplicazioni operative:

- `TabellaEsiste(...)`: se una tabella esiste gia, non viene ricreata;
- `CampoEsiste(...)`: verifica che una tabella esistente abbia almeno i campi minimi attesi;
- `IndiceEsiste(...)`: se un indice esiste gia, non viene ricreato;
- `CatalogoSottofaseEsiste(...)`: se una voce catalogo esiste gia, non viene reinserita.

Nota importante: se una tabella esiste gia ma con struttura diversa, lo script non la modifica. In quel caso si interrompe sui campi mancanti e richiede analisi manuale.

## 7. Lo script non deve essere eseguito automaticamente

Questo script non deve essere collegato a:

- macro automatiche;
- apertura database;
- pulsanti di produzione;
- avvio di FastAPI;
- avvio di Flask;
- flusso Grisu.

Deve essere eseguito manualmente da un operatore consapevole, dopo backup e verifica su copia del database.

## 8. Uso previsto in Access

Procedura consigliata per prima prova:

1. creare una copia locale non sincronizzata del database Access;
2. aprire la copia;
3. aprire l'editor VBA;
4. creare un nuovo modulo standard;
5. copiare lo script completo;
6. lasciare `USA_DATABASE_TARGET_ESTERNO = False`;
7. verificare che il riferimento DAO sia disponibile;
8. eseguire manualmente `CreaSchemaWorkflowProcedimento_MVP`;
9. controllare tabelle, indici e righe catalogo.

Procedura consigliata per applicazione reale piu prudente:

1. creare un database Access utility separato;
2. copiare lo script nel database utility;
3. impostare `USA_DATABASE_TARGET_ESTERNO = True`;
4. impostare `PERCORSO_DATABASE_TARGET` con il path del database target;
5. chiudere il database target;
6. verificare che non esista il file `.laccdb` del target;
7. eseguire manualmente `CreaSchemaWorkflowProcedimento_MVP`.

Compatibilita DAO VBA:

- lo script usa `DAO.Database`, `DAO.TableDef`, `DAO.Field`, `DAO.Index`, `DAO.QueryDef` e `DAO.Recordset`;
- in Access deve essere disponibile il riferimento DAO/Access Database Engine Object Library;
- se l'editor VBA segnala errore sui tipi `DAO.*`, verificare i riferimenti del progetto VBA prima di eseguire lo script.

## 9. Rollback manuale

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

Se sono state create relazioni Access manuali/grafiche, rimuoverle prima del `DROP TABLE`; Access puo impedire la cancellazione di tabelle referenziate da relazioni ancora presenti.

## 10. Checklist post-esecuzione

Dopo l'esecuzione reale, verificare:

- [ ] La cartella `Backup` esiste accanto al file `.accdb`.
- [ ] Il backup con timestamp e stato creato.
- [ ] Il backup ha dimensione maggiore di zero.
- [ ] Il backup ha dimensione uguale al file sorgente, se verificabile.
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
- [ ] Il flusso Flask/Grisu continua ad acquisire protocolli.
