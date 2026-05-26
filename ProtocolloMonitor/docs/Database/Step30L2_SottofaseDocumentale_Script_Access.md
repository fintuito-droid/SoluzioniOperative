# Step 30L-2 - Script Access Sottofase Documentale

## 1. Premessa operativa

Questo documento contiene lo script VBA operativo per predisporre il modello documentale della sottofase nel database Access di ProtocolloMonitor.

Lo script parte dallo schema progettato in:

```text
docs/Database/Step30L1_SottofaseDocumentale_Access_DDL.md
```

Lo script e pensato per essere copiato manualmente in un modulo VBA standard di Microsoft Access ed eseguito solo dopo verifica tecnica su una copia locale del database, preferibilmente non sincronizzata con OneDrive o altri sistemi cloud.

Questo documento non esegue alcuna modifica al database.

## 2. Oggetti gestiti dallo script

Lo script prepara:

- estensione della tabella esistente `T_ProcedimentoSottofasi`;
- nuova tabella `T_SottofaseDocumenti`;
- nuova tabella `T_SottofaseStepOperativi`;
- indici consigliati;
- controlli anti-duplicazione su campi, tabelle e indici.

Lo script non crea step operativi per le sottofasi gia esistenti. La generazione dei cinque step `REDIGI`, `REVISIONA`, `FIRMA`, `PROTOCOLLA`, `FINE` per ogni sottofase dovra essere gestita in uno step applicativo successivo, per evitare scritture massive non controllate.

## 3. Modalita operative supportate

Lo script distingue due scenari.

### A. Esecuzione dentro una copia Access aperta

Questa modalita e adatta alla prima prova manuale.

In questo caso il file `.laccdb` accanto al database puo essere normale, perche generato dalla sessione Access corrente. Lo script quindi non blocca automaticamente l'esecuzione solo perche esiste il lock del database corrente.

Attenzione: se lo script viene eseguito nel database corrente aperto, il backup prodotto tramite copia file e meno forte rispetto a un backup eseguito su database target chiuso. La copia puo risultare valida, ma il database e comunque in uso dalla sessione Access corrente.

Resta obbligatorio:

- lavorare inizialmente solo su una copia del database `.accdb`;
- creare e verificare il backup prima di qualsiasi DDL;
- interrompere se il backup fallisce;
- non usare questa modalita sul database runtime senza test precedente.

### B. Esecuzione da database utility verso database target chiuso

Questa e la modalita piu prudente per una futura applicazione reale.

Si crea un piccolo database Access di utilita, si copia lo script in quel database, si imposta `USA_DATABASE_TARGET_ESTERNO = True` e si valorizza `PERCORSO_DATABASE_TARGET`.

In questa modalita la presenza del file `.laccdb` del database target e un segnale di rischio e lo script si deve fermare.

Per l'applicazione reale sul database runtime e preferibile usare questa modalita: database utility esterno aperto, database `.accdb` target chiuso, backup verificato prima di qualsiasi modifica.

## 4. Regola obbligatoria di sicurezza

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

Raccomandazione forte: prima dell'applicazione reale eseguire almeno un test completo su copia locale non sincronizzata, verificando apertura tabelle, campi, indici e lettura da backend.

## 5. Note rischi prima dell'esecuzione

Rischi operativi da verificare prima dell'esecuzione reale:

- database sincronizzato con OneDrive o altri sistemi cloud;
- presenza del file di lock `.laccdb` non riconducibile alla sessione Access corrente;
- antivirus o sistemi di protezione endpoint che intercettano la copia del file;
- database aperto in modalita esclusiva da Access o da un altro utente;
- backup del database aperto: se la copia file fallisce o la dimensione non torna, lo script deve interrompersi;
- DDL Access non transazionale come PostgreSQL: se lo script fallisce a meta, possono restare campi, tabelle o indici gia creati.
- relazioni Access non create automaticamente: l'integrita iniziale tra sottofasi, documenti e step sara garantita dal backend.
- valori ammessi non vincolati dal motore Access: gli stati e gli step saranno inizialmente validati dal backend.

## 6. Script VBA completo

> Copiare il codice seguente in un modulo VBA Access.
>
> Non viene eseguito automaticamente.
>
> Avviare manualmente la macro `CreaSchemaSottofaseDocumentale_MVP`.

```vba
Option Compare Database
Option Explicit

' =============================================================================
' ProtocolloMonitor - Creazione schema MVP Sottofase Documentale
' =============================================================================
'
' SCOPO
' -----
' Estende il workflow procedimento con il modello documentale della sottofase.
'
' Oggetti gestiti:
' - T_ProcedimentoSottofasi: aggiunta campi documentali leggeri;
' - T_SottofaseDocumenti: documenti collegati alla sottofase;
' - T_SottofaseStepOperativi: ciclo interno REDIGI/REVISIONA/FIRMA/PROTOCOLLA/FINE.
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
' - se un campo esiste gia, non viene ricreato;
' - se una tabella esiste gia, non viene ricreata;
' - se un indice esiste gia, non viene ricreato.
'
' Se una tabella esiste ma ha struttura non conforme, lo script non prova a
' correggerla automaticamente: segnala errore sui campi mancanti.
'
' =============================================================================

Private Const USA_DATABASE_TARGET_ESTERNO As Boolean = False
Private Const PERCORSO_DATABASE_TARGET As String = ""

Public Sub CreaSchemaSottofaseDocumentale_MVP()
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
            Err.Raise vbObjectError + 4000, , "PERCORSO_DATABASE_TARGET non configurato."
        End If

        If Dir(percorsoDatabase) = "" Then
            Err.Raise vbObjectError + 4001, , "Database target non trovato: " & percorsoDatabase
        End If
    Else
        Set db = CurrentDb
        percorsoDatabase = CurrentDb.Name
        lockConsentitoSessioneCorrente = True

        If Len(Trim$(percorsoDatabase)) = 0 Then
            Err.Raise vbObjectError + 4002, , "Percorso database corrente non disponibile."
        End If
    End If

    VerificaLockDatabase percorsoDatabase, lockConsentitoSessioneCorrente

    percorsoBackup = CreaBackupDatabaseCorrente(percorsoDatabase)
    VerificaBackupDatabase percorsoDatabase, percorsoBackup

    If USA_DATABASE_TARGET_ESTERNO Then
        Set db = DBEngine.Workspaces(0).OpenDatabase(percorsoDatabase)
        databaseEsternoAperto = True
    End If

    VerificaPrerequisitiWorkflow db

    EstendiTabellaProcedimentoSottofasi db
    CreaTabellaSottofaseDocumenti db
    CreaTabellaSottofaseStepOperativi db

    VerificaStrutturaSottofaseDocumentale db

    CreaIndiciProcedimentoSottofasiDocumentale db
    CreaIndiciSottofaseDocumenti db
    CreaIndiciSottofaseStepOperativi db

    If databaseEsternoAperto Then
        db.Close
        databaseEsternoAperto = False
    End If

    MsgBox _
        "Schema Sottofase Documentale creato/verificato correttamente." & vbCrLf & _
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
        "Errore durante la creazione schema Sottofase Documentale." & vbCrLf & _
        "Numero errore: " & Err.Number & vbCrLf & _
        "Descrizione: " & Err.Description, _
        vbCritical, _
        "ProtocolloMonitor"
End Sub

Private Function CreaBackupDatabaseCorrente(ByVal percorsoDatabase As String) As String
    Dim fso As Object
    Dim cartellaDatabase As String
    Dim cartellaBackup As String
    Dim nomeBase As String
    Dim estensione As String
    Dim timestamp As String
    Dim percorsoBackup As String

    Set fso = CreateObject("Scripting.FileSystemObject")

    cartellaDatabase = fso.GetParentFolderName(percorsoDatabase)
    nomeBase = fso.GetBaseName(percorsoDatabase)
    estensione = fso.GetExtensionName(percorsoDatabase)

    If Len(cartellaDatabase) = 0 Then
        Err.Raise vbObjectError + 4100, , "Impossibile individuare la cartella del database."
    End If

    cartellaBackup = fso.BuildPath(cartellaDatabase, "Backup")

    If Not fso.FolderExists(cartellaBackup) Then
        fso.CreateFolder cartellaBackup
    End If

    timestamp = Format$(Now, "yyyymmdd_hhnnss")
    percorsoBackup = fso.BuildPath( _
        cartellaBackup, _
        nomeBase & "_BACKUP_" & timestamp & "." & estensione _
    )

    fso.CopyFile percorsoDatabase, percorsoBackup, False

    CreaBackupDatabaseCorrente = percorsoBackup
End Function

Private Sub VerificaBackupDatabase( _
    ByVal percorsoDatabase As String, _
    ByVal percorsoBackup As String _
)
    Dim fso As Object
    Dim dimensioneOrigine As Currency
    Dim dimensioneBackup As Currency

    Set fso = CreateObject("Scripting.FileSystemObject")

    If Not fso.FileExists(percorsoBackup) Then
        Err.Raise vbObjectError + 4200, , "Backup non creato: " & percorsoBackup
    End If

    dimensioneBackup = fso.GetFile(percorsoBackup).Size

    If dimensioneBackup <= 0 Then
        Err.Raise vbObjectError + 4201, , "Backup creato ma dimensione pari a zero."
    End If

    If fso.FileExists(percorsoDatabase) Then
        dimensioneOrigine = fso.GetFile(percorsoDatabase).Size

        If dimensioneOrigine > 0 Then
            If dimensioneBackup <> dimensioneOrigine Then
                Err.Raise vbObjectError + 4202, , _
                    "Dimensione backup diversa dal database sorgente. " & _
                    "Origine=" & CStr(dimensioneOrigine) & _
                    " Backup=" & CStr(dimensioneBackup)
            End If
        End If
    End If
End Sub

Private Sub VerificaLockDatabase( _
    ByVal percorsoDatabase As String, _
    ByVal lockConsentitoSessioneCorrente As Boolean _
)
    Dim fso As Object
    Dim cartellaDatabase As String
    Dim nomeBase As String
    Dim percorsoLock As String

    Set fso = CreateObject("Scripting.FileSystemObject")

    cartellaDatabase = fso.GetParentFolderName(percorsoDatabase)
    nomeBase = fso.GetBaseName(percorsoDatabase)
    percorsoLock = fso.BuildPath(cartellaDatabase, nomeBase & ".laccdb")

    If fso.FileExists(percorsoLock) Then
        If Not lockConsentitoSessioneCorrente Then
            Err.Raise vbObjectError + 4300, , _
                "File lock .laccdb presente sul database target chiuso: " & percorsoLock
        End If
    End If
End Sub

Private Sub VerificaPrerequisitiWorkflow(ByVal db As DAO.Database)
    If Not TabellaEsiste(db, "T_ProcedimentoSottofasi") Then
        Err.Raise vbObjectError + 4400, , _
            "La tabella T_ProcedimentoSottofasi non esiste. " & _
            "Applicare prima lo schema workflow procedimento."
    End If

    VerificaCampiRichiesti db, "T_ProcedimentoSottofasi", Array( _
        "IDSottofase", "IDFase", "CodiceSottofase", "Titolo", _
        "Ordine", "StatoSottofase", "Attivo", "DataCreazione", "DataModifica" _
    )
End Sub

Private Sub EstendiTabellaProcedimentoSottofasi(ByVal db As DAO.Database)
    AggiungiCampoSeAssente db, "T_ProcedimentoSottofasi", "StepCorrente", "TEXT(50)"
    AggiungiCampoSeAssente db, "T_ProcedimentoSottofasi", "TestoOperatore", "MEMO"
    AggiungiCampoSeAssente db, "T_ProcedimentoSottofasi", "HaDocumentoCollegato", "YESNO"
    AggiungiCampoSeAssente db, "T_ProcedimentoSottofasi", "IDDocumentoCorrente", "LONG"
    AggiungiCampoSeAssente db, "T_ProcedimentoSottofasi", "DataUltimaAzione", "DATETIME"
    AggiungiCampoSeAssente db, "T_ProcedimentoSottofasi", "UtenteUltimaAzione", "TEXT(100)"
    AggiungiCampoSeAssente db, "T_ProcedimentoSottofasi", "VersioneDocumento", "INTEGER"
End Sub

Private Sub CreaTabellaSottofaseDocumenti(ByVal db As DAO.Database)
    If TabellaEsiste(db, "T_SottofaseDocumenti") Then
        Exit Sub
    End If

    db.Execute _
        "CREATE TABLE [T_SottofaseDocumenti] (" & _
        "[IDDocumentoSottofase] COUNTER CONSTRAINT [PK_T_SottofaseDocumenti] PRIMARY KEY, " & _
        "[IDSottofase] LONG, " & _
        "[TipoDocumento] TEXT(50), " & _
        "[NomeFile] TEXT(255), " & _
        "[Estensione] TEXT(20), " & _
        "[PercorsoDocumento] MEMO, " & _
        "[MimeType] TEXT(100), " & _
        "[DimensioneBytes] LONG, " & _
        "[HashFile] TEXT(128), " & _
        "[VersioneDocumento] INTEGER, " & _
        "[DataCollegamento] DATETIME, " & _
        "[UtenteCollegamento] TEXT(100), " & _
        "[Attivo] YESNO, " & _
        "[DataCreazione] DATETIME, " & _
        "[DataModifica] DATETIME" & _
        ")", _
        dbFailOnError
End Sub

Private Sub CreaTabellaSottofaseStepOperativi(ByVal db As DAO.Database)
    If TabellaEsiste(db, "T_SottofaseStepOperativi") Then
        Exit Sub
    End If

    db.Execute _
        "CREATE TABLE [T_SottofaseStepOperativi] (" & _
        "[IDStepSottofase] COUNTER CONSTRAINT [PK_T_SottofaseStepOperativi] PRIMARY KEY, " & _
        "[IDSottofase] LONG, " & _
        "[CodiceStep] TEXT(50), " & _
        "[Ordine] INTEGER, " & _
        "[StatoStep] TEXT(50), " & _
        "[DataAvvio] DATETIME, " & _
        "[DataCompletamento] DATETIME, " & _
        "[NoteStep] MEMO, " & _
        "[UtenteAssegnato] TEXT(100), " & _
        "[UtenteCompletamento] TEXT(100), " & _
        "[IDDocumentoSottofase] LONG, " & _
        "[VersioneDocumento] INTEGER, " & _
        "[DataCreazione] DATETIME, " & _
        "[DataModifica] DATETIME" & _
        ")", _
        dbFailOnError
End Sub

Private Sub VerificaStrutturaSottofaseDocumentale(ByVal db As DAO.Database)
    VerificaCampiRichiesti db, "T_ProcedimentoSottofasi", Array( _
        "StepCorrente", "TestoOperatore", "HaDocumentoCollegato", _
        "IDDocumentoCorrente", "DataUltimaAzione", "UtenteUltimaAzione", _
        "VersioneDocumento" _
    )

    VerificaCampiRichiesti db, "T_SottofaseDocumenti", Array( _
        "IDDocumentoSottofase", "IDSottofase", "TipoDocumento", "NomeFile", _
        "Estensione", "PercorsoDocumento", "MimeType", "DimensioneBytes", _
        "HashFile", "VersioneDocumento", "DataCollegamento", _
        "UtenteCollegamento", "Attivo", "DataCreazione", "DataModifica" _
    )

    VerificaCampiRichiesti db, "T_SottofaseStepOperativi", Array( _
        "IDStepSottofase", "IDSottofase", "CodiceStep", "Ordine", _
        "StatoStep", "DataAvvio", "DataCompletamento", "NoteStep", _
        "UtenteAssegnato", "UtenteCompletamento", "IDDocumentoSottofase", _
        "VersioneDocumento", "DataCreazione", "DataModifica" _
    )
End Sub

Private Sub CreaIndiciProcedimentoSottofasiDocumentale(ByVal db As DAO.Database)
    VerificaCampiRichiesti db, "T_ProcedimentoSottofasi", Array( _
        "StepCorrente", "HaDocumentoCollegato", "IDDocumentoCorrente", _
        "DataUltimaAzione" _
    )

    CreaIndiceSeAssente db, _
        "T_ProcedimentoSottofasi", _
        "IX_T_ProcedimentoSottofasi_StepCorrente", _
        False, _
        "StepCorrente"

    CreaIndiceSeAssente db, _
        "T_ProcedimentoSottofasi", _
        "IX_T_ProcedimentoSottofasi_HaDocumento", _
        False, _
        "HaDocumentoCollegato"

    CreaIndiceSeAssente db, _
        "T_ProcedimentoSottofasi", _
        "IX_T_ProcedimentoSottofasi_DocumentoCorrente", _
        False, _
        "IDDocumentoCorrente"

    CreaIndiceSeAssente db, _
        "T_ProcedimentoSottofasi", _
        "IX_T_ProcedimentoSottofasi_DataUltimaAzione", _
        False, _
        "DataUltimaAzione"
End Sub

Private Sub CreaIndiciSottofaseDocumenti(ByVal db As DAO.Database)
    VerificaCampiRichiesti db, "T_SottofaseDocumenti", Array( _
        "IDSottofase", "TipoDocumento", "Attivo", _
        "DataCollegamento", "VersioneDocumento" _
    )

    CreaIndiceSeAssente db, "T_SottofaseDocumenti", _
        "IX_T_SottofaseDocumenti_IDSottofase", False, "IDSottofase"

    CreaIndiceSeAssente db, "T_SottofaseDocumenti", _
        "IX_T_SottofaseDocumenti_TipoDocumento", False, "TipoDocumento"

    CreaIndiceSeAssente db, "T_SottofaseDocumenti", _
        "IX_T_SottofaseDocumenti_Attivo", False, "Attivo"

    CreaIndiceSeAssente db, "T_SottofaseDocumenti", _
        "IX_T_SottofaseDocumenti_DataCollegamento", False, "DataCollegamento"

    CreaIndiceSeAssente db, "T_SottofaseDocumenti", _
        "IX_T_SottofaseDocumenti_Versione", False, "IDSottofase", "VersioneDocumento"
End Sub

Private Sub CreaIndiciSottofaseStepOperativi(ByVal db As DAO.Database)
    VerificaCampiRichiesti db, "T_SottofaseStepOperativi", Array( _
        "IDSottofase", "CodiceStep", "Ordine", "StatoStep", _
        "IDDocumentoSottofase" _
    )

    CreaIndiceSeAssente db, "T_SottofaseStepOperativi", _
        "IX_T_SottofaseStepOperativi_IDSottofase", False, "IDSottofase"

    CreaIndiceSeAssente db, "T_SottofaseStepOperativi", _
        "IX_T_SottofaseStepOperativi_Ordine", False, "IDSottofase", "Ordine"

    CreaIndiceSeAssente db, "T_SottofaseStepOperativi", _
        "IX_T_SottofaseStepOperativi_CodiceStep", False, "CodiceStep"

    CreaIndiceSeAssente db, "T_SottofaseStepOperativi", _
        "IX_T_SottofaseStepOperativi_StatoStep", False, "StatoStep"

    CreaIndiceSeAssente db, "T_SottofaseStepOperativi", _
        "IX_T_SottofaseStepOperativi_Documento", False, "IDDocumentoSottofase"
End Sub

Private Sub AggiungiCampoSeAssente( _
    ByVal db As DAO.Database, _
    ByVal nomeTabella As String, _
    ByVal nomeCampo As String, _
    ByVal tipoCampo As String _
)
    If Not TabellaEsiste(db, nomeTabella) Then
        Err.Raise vbObjectError + 4500, , "Tabella non trovata: " & nomeTabella
    End If

    If CampoEsiste(db, nomeTabella, nomeCampo) Then
        Exit Sub
    End If

    db.Execute _
        "ALTER TABLE [" & nomeTabella & "] ADD COLUMN [" & nomeCampo & "] " & tipoCampo, _
        dbFailOnError
End Sub

Private Sub CreaIndiceSeAssente( _
    ByVal db As DAO.Database, _
    ByVal nomeTabella As String, _
    ByVal nomeIndice As String, _
    ByVal univoco As Boolean, _
    ParamArray nomiCampi() As Variant _
)
    Dim sql As String
    Dim elencoCampi As String
    Dim i As Long

    If Not TabellaEsiste(db, nomeTabella) Then
        Err.Raise vbObjectError + 4600, , _
            "Impossibile creare indice. Tabella non trovata: " & nomeTabella
    End If

    If IndiceEsiste(db, nomeTabella, nomeIndice) Then
        Exit Sub
    End If

    For i = LBound(nomiCampi) To UBound(nomiCampi)
        If Not CampoEsiste(db, nomeTabella, CStr(nomiCampi(i))) Then
            Err.Raise vbObjectError + 4601, , _
                "Impossibile creare indice " & nomeIndice & _
                ". Campo mancante: " & CStr(nomiCampi(i))
        End If

        If Len(elencoCampi) > 0 Then
            elencoCampi = elencoCampi & ", "
        End If

        elencoCampi = elencoCampi & "[" & CStr(nomiCampi(i)) & "]"
    Next i

    If univoco Then
        sql = "CREATE UNIQUE INDEX [" & nomeIndice & "] ON [" & nomeTabella & "] (" & elencoCampi & ")"
    Else
        sql = "CREATE INDEX [" & nomeIndice & "] ON [" & nomeTabella & "] (" & elencoCampi & ")"
    End If

    db.Execute sql, dbFailOnError
End Sub

Private Sub VerificaCampiRichiesti( _
    ByVal db As DAO.Database, _
    ByVal nomeTabella As String, _
    ByVal campiRichiesti As Variant _
)
    Dim i As Long
    Dim nomeCampo As String

    If Not TabellaEsiste(db, nomeTabella) Then
        Err.Raise vbObjectError + 4700, , "Tabella richiesta non trovata: " & nomeTabella
    End If

    For i = LBound(campiRichiesti) To UBound(campiRichiesti)
        nomeCampo = CStr(campiRichiesti(i))

        If Not CampoEsiste(db, nomeTabella, nomeCampo) Then
            Err.Raise vbObjectError + 4701, , _
                "Struttura non conforme. Tabella=" & nomeTabella & _
                " Campo mancante=" & nomeCampo
        End If
    Next i
End Sub

Private Function TabellaEsiste( _
    ByVal db As DAO.Database, _
    ByVal nomeTabella As String _
) As Boolean
    Dim tdf As DAO.TableDef

    TabellaEsiste = False

    For Each tdf In db.TableDefs
        If StrComp(tdf.Name, nomeTabella, vbTextCompare) = 0 Then
            TabellaEsiste = True
            Exit Function
        End If
    Next tdf
End Function

Private Function CampoEsiste( _
    ByVal db As DAO.Database, _
    ByVal nomeTabella As String, _
    ByVal nomeCampo As String _
) As Boolean
    Dim tdf As DAO.TableDef
    Dim fld As DAO.Field

    CampoEsiste = False

    If Not TabellaEsiste(db, nomeTabella) Then
        Exit Function
    End If

    Set tdf = db.TableDefs(nomeTabella)

    For Each fld In tdf.Fields
        If StrComp(fld.Name, nomeCampo, vbTextCompare) = 0 Then
            CampoEsiste = True
            Exit Function
        End If
    Next fld
End Function

Private Function IndiceEsiste( _
    ByVal db As DAO.Database, _
    ByVal nomeTabella As String, _
    ByVal nomeIndice As String _
) As Boolean
    Dim tdf As DAO.TableDef
    Dim idx As DAO.Index

    IndiceEsiste = False

    If Not TabellaEsiste(db, nomeTabella) Then
        Exit Function
    End If

    Set tdf = db.TableDefs(nomeTabella)

    For Each idx In tdf.Indexes
        If StrComp(idx.Name, nomeIndice, vbTextCompare) = 0 Then
            IndiceEsiste = True
            Exit Function
        End If
    Next idx
End Function
```

## 7. Valori applicativi previsti

Lo script non inserisce righe in `T_SottofaseStepOperativi`, ma il backend dovra usare questi valori standard quando inizializzera gli step di una sottofase documentale.

Access non applica in questo script vincoli `CHECK` sui valori ammessi. La validazione iniziale sara quindi responsabilita del backend, in modo da mantenere lo schema prudente oggi e PostgreSQL-friendly domani.

### CodiceStep

| CodiceStep | Ordine |
| --- | --- |
| `REDIGI` | 10 |
| `REVISIONA` | 20 |
| `FIRMA` | 30 |
| `PROTOCOLLA` | 40 |
| `FINE` | 50 |

### StatoStep

| StatoStep | Significato |
| --- | --- |
| `NON_AVVIATO` | Step previsto ma non ancora iniziato. |
| `IN_CORSO` | Step in lavorazione. |
| `COMPLETATO` | Step completato. |
| `BLOCCATO` | Step non completabile per anomalia o dipendenza. |

## 8. Default applicativi richiesti al backend

Lo script non imposta default Access sui nuovi campi, per evitare comportamenti impliciti difficili da governare durante la futura migrazione PostgreSQL.

Il backend dovra valorizzare esplicitamente almeno:

| Campo | Valore applicativo consigliato |
| --- | --- |
| `T_ProcedimentoSottofasi.HaDocumentoCollegato` | `False` quando una sottofase viene creata senza documento. |
| `T_SottofaseDocumenti.Attivo` | `True` quando viene registrato un documento corrente/valido. |
| `DataCreazione` | `Now()` al momento dell'inserimento record. |
| `DataModifica` | `Now()` al momento dell'inserimento e di ogni aggiornamento record. |

Questa scelta rende piu espliciti repository e service layer: ogni scrittura futura dovra dichiarare cosa sta creando o aggiornando, senza dipendere da automatismi Access.

## 9. Relazioni Access

Lo script non crea volutamente relazioni Access fisiche tra:

- `T_ProcedimentoSottofasi`;
- `T_SottofaseDocumenti`;
- `T_SottofaseStepOperativi`.

La scelta e prudente per l'MVP perche riduce il rischio di blocchi o errori su un database Access gia in uso. L'integrita iniziale sara garantita dal backend:

- un documento dovra riferirsi a una sottofase esistente;
- uno step operativo dovra riferirsi a una sottofase esistente;
- il documento corrente della sottofase dovra riferirsi a un documento esistente e attivo;
- cancellazioni fisiche non dovranno essere introdotte senza regole chiare.

In PostgreSQL sara opportuno introdurre foreign key reali, vincoli `CHECK` sugli stati e transazioni per ogni operazione composta.

## 10. Controlli anti-duplicazione

Lo script include:

- `AggiungiCampoSeAssente(...)`: aggiunge un campo solo se non esiste;
- `TabellaEsiste(...)`: evita di ricreare tabelle esistenti;
- `CampoEsiste(...)`: valida campi prima di alter table e indici;
- `IndiceEsiste(...)`: evita di ricreare indici esistenti;
- `VerificaCampiRichiesti(...)`: blocca lo script se una tabella esistente non e conforme.

Se una tabella esiste gia, lo script non la modifica automaticamente oltre alla verifica dei campi richiesti. In caso di struttura non conforme, serve revisione manuale.

## 11. Strategia Word Desktop

Questo script prepara solo lo schema dati.

Il flusso operativo futuro consigliato e:

1. l'utente clicca `Redigi`;
2. il frontend chiede di selezionare un file Word;
3. il backend registra il file in `T_SottofaseDocumenti`;
4. il backend aggiorna `T_ProcedimentoSottofasi.IDDocumentoCorrente`;
5. il backend aggiorna `StepCorrente`;
6. il frontend mostra icona documento se `HaDocumentoCollegato = True`;
7. l'apertura file avviene tramite backend Windows controllato.

Il browser non deve ricevere path arbitrari da aprire direttamente. Tutte le aperture locali devono passare da endpoint backend con normalizzazione e controllo del percorso.

## 12. Rollback manuale

Access non tratta il DDL in modo transazionale come PostgreSQL. Il rollback piu sicuro resta il ripristino del backup creato prima dell'esecuzione.

Se fosse necessario un rollback manuale:

1. rimuovere eventuali relazioni Access manuali/grafiche;
2. eliminare indici sulle nuove tabelle;
3. eliminare `T_SottofaseStepOperativi`;
4. eliminare `T_SottofaseDocumenti`;
5. valutare con estrema prudenza la rimozione dei campi aggiunti a `T_ProcedimentoSottofasi`.

Esempio concettuale:

```sql
DROP TABLE T_SottofaseStepOperativi;
DROP TABLE T_SottofaseDocumenti;
```

I campi aggiunti a `T_ProcedimentoSottofasi` non vanno rimossi se nel frattempo sono stati popolati, per evitare perdita dati. In quel caso e preferibile ripristinare il backup.

## 13. Checklist post-esecuzione

Dopo una futura esecuzione reale, verificare manualmente:

- [ ] backup creato con timestamp;
- [ ] backup esistente;
- [ ] backup con dimensione maggiore di zero;
- [ ] backup con dimensione uguale al database sorgente;
- [ ] `T_ProcedimentoSottofasi.StepCorrente` presente;
- [ ] `T_ProcedimentoSottofasi.TestoOperatore` presente;
- [ ] `T_ProcedimentoSottofasi.HaDocumentoCollegato` presente;
- [ ] `T_ProcedimentoSottofasi.IDDocumentoCorrente` presente;
- [ ] `T_ProcedimentoSottofasi.DataUltimaAzione` presente;
- [ ] `T_ProcedimentoSottofasi.UtenteUltimaAzione` presente;
- [ ] `T_ProcedimentoSottofasi.VersioneDocumento` presente;
- [ ] `T_SottofaseDocumenti` presente;
- [ ] `T_SottofaseStepOperativi` presente;
- [ ] indici `IX_T_SottofaseDocumenti_*` presenti;
- [ ] indici `IX_T_SottofaseStepOperativi_*` presenti;
- [ ] indici documentali su `T_ProcedimentoSottofasi` presenti;
- [ ] nessun errore Access durante apertura tabelle;
- [ ] nessun file `.laccdb` residuo anomalo dopo la chiusura del database.

## 14. Prossimi passi consigliati

1. Revisione tecnica dello script VBA.
2. Eventuale correzione documento script.
3. Applicazione reale solo dopo backup verificato.
4. Repository/service read-only per documenti e step sottofase.
5. API read-only.
6. UI read-only del ciclo `REDIGI > REVISIONA > FIRMA > PROTOCOLLA > FINE`.
7. Prima scrittura controllata: collegamento documento Word alla sottofase.
