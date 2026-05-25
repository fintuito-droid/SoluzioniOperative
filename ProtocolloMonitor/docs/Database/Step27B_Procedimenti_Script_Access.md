# Step 27B - Script Access Procedimenti

## 1. Premessa operativa

Questo documento contiene uno script VBA operativo per creare le tabelle MVP dell'entita `Procedimento` nel database Access di ProtocolloMonitor.

Lo script e pensato per essere copiato manualmente in un modulo VBA di Microsoft Access ed eseguito solo dopo verifica tecnica.

Questo documento non esegue alcuna modifica al database.

Tabelle previste:

- `T_Procedimenti`
- `T_ProcedimentoProtocolli`

Indici previsti:

- indici di ricerca su codice, soggetto, comando, settore, stato, priorita e scadenza;
- indici sulla tabella ponte;
- indice univoco sulla coppia `IDProcedimento`, `IDProtocollo`.

## 2. Regola obbligatoria di sicurezza

Prima di eseguire qualsiasi modifica reale al file `.accdb` deve essere creato un backup con data e ora nel nome file.

Formato consigliato:

```text
Backup\NomeDatabase_YYYYMMDD_HHNNSS.accdb
```

Se la creazione del backup fallisce, lo script deve fermarsi immediatamente.

Non procedere mai alla creazione di tabelle o indici se:

- il percorso del database non e identificabile;
- la cartella `Backup` non puo essere creata;
- la copia del file `.accdb` non riesce;
- il file copiato non esiste dopo la copia.

## 3. Script VBA completo

> Copiare il codice seguente in un modulo VBA Access.
>
> Non viene eseguito automaticamente.
>
> Avviare manualmente la macro `CreaSchemaProcedimenti_MVP`.

```vba
Option Compare Database
Option Explicit

' =============================================================================
' ProtocolloMonitor - Creazione schema MVP Procedimenti
' =============================================================================
'
' SCOPO
' -----
' Crea le tabelle Access:
' - T_Procedimenti
' - T_ProcedimentoProtocolli
'
' Prima di modificare il database, crea un backup del file .accdb corrente.
'
' SICUREZZA
' ---------
' Se il backup non riesce o non viene verificato, lo script si interrompe.
'
' NOTE
' ----
' Lo script e idempotente a livello operativo:
' - se una tabella esiste gia, non viene ricreata;
' - se un indice esiste gia, non viene ricreato.
'
' =============================================================================

Public Sub CreaSchemaProcedimenti_MVP()
    On Error GoTo GestioneErrore

    Dim db As DAO.Database
    Dim percorsoDatabase As String
    Dim percorsoBackup As String

    Set db = CurrentDb
    percorsoDatabase = CurrentDb.Name

    If Len(Trim$(percorsoDatabase)) = 0 Then
        Err.Raise vbObjectError + 1000, , "Percorso database corrente non disponibile."
    End If

    percorsoBackup = CreaBackupDatabaseCorrente(percorsoDatabase)

    If Len(Trim$(percorsoBackup)) = 0 Then
        Err.Raise vbObjectError + 1001, , "Backup non creato. Creazione schema interrotta."
    End If

    If Dir(percorsoBackup) = "" Then
        Err.Raise vbObjectError + 1002, , "Backup non verificabile. Creazione schema interrotta."
    End If

    CreaTabellaProcedimenti db
    CreaTabellaProcedimentoProtocolli db
    CreaIndiciProcedimenti db
    CreaIndiciProcedimentoProtocolli db

    MsgBox _
        "Schema Procedimenti creato/verificato correttamente." & vbCrLf & _
        "Backup creato in:" & vbCrLf & percorsoBackup, _
        vbInformation, _
        "ProtocolloMonitor"

    Exit Sub

GestioneErrore:
    MsgBox _
        "Errore durante la creazione schema Procedimenti." & vbCrLf & _
        "Numero errore: " & Err.Number & vbCrLf & _
        "Descrizione: " & Err.Description, _
        vbCritical, _
        "ProtocolloMonitor"
End Sub


Private Function CreaBackupDatabaseCorrente(ByVal percorsoDatabase As String) As String
    On Error GoTo GestioneErrore

    Dim fso As Object
    Dim cartellaDatabase As String
    Dim nomeDatabase As String
    Dim nomeSenzaEstensione As String
    Dim estensione As String
    Dim cartellaBackup As String
    Dim percorsoBackup As String
    Dim timestamp As String

    Set fso = CreateObject("Scripting.FileSystemObject")

    cartellaDatabase = fso.GetParentFolderName(percorsoDatabase)
    nomeDatabase = fso.GetFileName(percorsoDatabase)
    nomeSenzaEstensione = fso.GetBaseName(percorsoDatabase)
    estensione = fso.GetExtensionName(percorsoDatabase)

    If Len(Trim$(cartellaDatabase)) = 0 Then
        Err.Raise vbObjectError + 1100, , "Cartella database non identificabile."
    End If

    If Len(Trim$(nomeDatabase)) = 0 Then
        Err.Raise vbObjectError + 1101, , "Nome database non identificabile."
    End If

    cartellaBackup = fso.BuildPath(cartellaDatabase, "Backup")

    If Not fso.FolderExists(cartellaBackup) Then
        fso.CreateFolder cartellaBackup
    End If

    timestamp = Format(Now, "yyyymmdd_hhnnss")
    percorsoBackup = fso.BuildPath(
        cartellaBackup,
        nomeSenzaEstensione & "_" & timestamp & "." & estensione
    )

    fso.CopyFile percorsoDatabase, percorsoBackup, False

    If Not fso.FileExists(percorsoBackup) Then
        Err.Raise vbObjectError + 1102, , "Il file backup non esiste dopo la copia."
    End If

    CreaBackupDatabaseCorrente = percorsoBackup
    Exit Function

GestioneErrore:
    CreaBackupDatabaseCorrente = ""
    Err.Raise Err.Number, , "Backup fallito: " & Err.Description
End Function


Private Sub CreaTabellaProcedimenti(ByVal db As DAO.Database)
    If TabellaEsiste(db, "T_Procedimenti") Then
        Exit Sub
    End If

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
        ")", _
        dbFailOnError
End Sub


Private Sub CreaTabellaProcedimentoProtocolli(ByVal db As DAO.Database)
    If TabellaEsiste(db, "T_ProcedimentoProtocolli") Then
        Exit Sub
    End If

    db.Execute _
        "CREATE TABLE T_ProcedimentoProtocolli (" & _
        "IDProcedimentoProtocollo AUTOINCREMENT CONSTRAINT PK_T_ProcedimentoProtocolli PRIMARY KEY, " & _
        "IDProcedimento LONG, " & _
        "IDProtocollo LONG, " & _
        "RuoloProtocollo TEXT(50), " & _
        "Principale YESNO, " & _
        "DataCollegamento DATETIME, " & _
        "NoteCollegamento LONGTEXT" & _
        ")", _
        dbFailOnError
End Sub


Private Sub CreaIndiciProcedimenti(ByVal db As DAO.Database)
    CreaIndiceSeAssente db, "T_Procedimenti", "IX_T_Procedimenti_CodiceProcedimento", "CodiceProcedimento", False
    CreaIndiceSeAssente db, "T_Procedimenti", "IX_T_Procedimenti_AziendaSoggetto", "AziendaSoggetto", False
    CreaIndiceSeAssente db, "T_Procedimenti", "IX_T_Procedimenti_ComandoCompetenza", "ComandoCompetenza", False
    CreaIndiceSeAssente db, "T_Procedimenti", "IX_T_Procedimenti_SettoreCompetenza", "SettoreCompetenza", False
    CreaIndiceSeAssente db, "T_Procedimenti", "IX_T_Procedimenti_StatoProcedimento", "StatoProcedimento", False
    CreaIndiceSeAssente db, "T_Procedimenti", "IX_T_Procedimenti_Priorita", "Priorita", False
    CreaIndiceSeAssente db, "T_Procedimenti", "IX_T_Procedimenti_DataScadenza", "DataScadenza", False
End Sub


Private Sub CreaIndiciProcedimentoProtocolli(ByVal db As DAO.Database)
    CreaIndiceSeAssente db, "T_ProcedimentoProtocolli", "IX_T_ProcedimentoProtocolli_IDProcedimento", "IDProcedimento", False
    CreaIndiceSeAssente db, "T_ProcedimentoProtocolli", "IX_T_ProcedimentoProtocolli_IDProtocollo", "IDProtocollo", False
    CreaIndiceSeAssente db, "T_ProcedimentoProtocolli", "UX_T_ProcedimentoProtocolli_Procedimento_Protocollo", "IDProcedimento, IDProtocollo", True
End Sub


Private Sub CreaIndiceSeAssente(
    ByVal db As DAO.Database,
    ByVal nomeTabella As String,
    ByVal nomeIndice As String,
    ByVal campiIndice As String,
    ByVal univoco As Boolean
)
    Dim sql As String

    If Not TabellaEsiste(db, nomeTabella) Then
        Err.Raise vbObjectError + 1200, , "Tabella non trovata per indice: " & nomeTabella
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


Private Function IndiceEsiste(
    ByVal db As DAO.Database,
    ByVal nomeTabella As String,
    ByVal nomeIndice As String
) As Boolean
    On Error GoTo NonEsiste

    Dim idx As DAO.Index
    Set idx = db.TableDefs(nomeTabella).Indexes(nomeIndice)

    IndiceEsiste = True
    Exit Function

NonEsiste:
    IndiceEsiste = False
End Function
```

## 4. Lo script non deve essere eseguito automaticamente

Questo script non deve essere collegato a:

- macro automatiche;
- apertura database;
- pulsanti di produzione;
- avvio di FastAPI;
- avvio di Flask/Grisù.

Deve essere eseguito manualmente da un operatore consapevole, dopo backup e verifica su copia del database.

## 5. Uso previsto in Access

Procedura consigliata:

1. aprire una copia del database Access;
2. aprire l'editor VBA;
3. creare un nuovo modulo standard;
4. copiare lo script completo;
5. verificare che il riferimento DAO sia disponibile;
6. eseguire manualmente `CreaSchemaProcedimenti_MVP`;
7. controllare tabelle, indici e messaggi.

## 6. Controlli anti-duplicazione

Lo script contiene:

- `TabellaEsiste(...)`;
- `IndiceEsiste(...)`;
- `CreaIndiceSeAssente(...)`.

Questi controlli evitano errori in caso di riesecuzione parziale.

Nota: se una tabella esiste gia ma con struttura diversa, lo script non la modifica. In quel caso serve analisi manuale.

## 7. Rollback manuale

Rollback preferito:

1. chiudere Access;
2. ripristinare il file `.accdb` dal backup creato dallo script;
3. riaprire il database ripristinato;
4. verificare che le tabelle precedenti siano presenti e funzionanti.

Rollback SQL manuale, solo se non ci sono dati da conservare:

```sql
DROP TABLE T_ProcedimentoProtocolli;
DROP TABLE T_Procedimenti;
```

Ordine importante:

1. eliminare prima `T_ProcedimentoProtocolli`;
2. eliminare poi `T_Procedimenti`.

Se sono state create relazioni Access manuali, rimuoverle prima del `DROP TABLE`.

## 8. Checklist post-esecuzione

Dopo l'esecuzione reale, verificare:

- [ ] La cartella `Backup` esiste accanto al file `.accdb`.
- [ ] Il backup con timestamp e stato creato.
- [ ] Il backup e apribile o copiabile.
- [ ] `T_Procedimenti` esiste.
- [ ] `T_ProcedimentoProtocolli` esiste.
- [ ] `IDProcedimento` e chiave primaria.
- [ ] `IDProcedimentoProtocollo` e chiave primaria.
- [ ] Gli indici `IX_T_Procedimenti_*` sono presenti.
- [ ] Gli indici `IX_T_ProcedimentoProtocolli_*` sono presenti.
- [ ] L'indice univoco `UX_T_ProcedimentoProtocolli_Procedimento_Protocollo` e presente.
- [ ] `T_Protocolli` non e stata modificata.
- [ ] Gli endpoint FastAPI esistenti continuano a funzionare.
- [ ] Il flusso Flask/Grisù continua ad acquisire protocolli.
- [ ] Il frontend continua a visualizzare elenco, dettaglio e PDF.

