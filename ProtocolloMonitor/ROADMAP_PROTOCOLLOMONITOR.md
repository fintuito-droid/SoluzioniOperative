# Roadmap tecnica ProtocolloMonitor

Documento riepilogativo della strategia adottata nello sviluppo di
ProtocolloMonitor, primo modulo operativo della piattaforma multi modulo
Soluzioni Operative.

Ultimo aggiornamento: 2026-05-27.

Fonte del riepilogo: analisi di codice, documentazione tecnica, test e storico
Git del progetto. Il database Access reale non e stato modificato per produrre
questo documento.

## 1. Architettura generale

ProtocolloMonitor e strutturato come modulo applicativo separato dentro
Soluzioni Operative.

| Area | Stato attuale | Strategia |
| --- | --- | --- |
| Frontend | Vue 3, Vuetify 4, Vue Router, viste operative in `frontend/src/views` e componenti riusabili in `frontend/src/components/procedimenti`. | UI progressiva: prima lettura, poi mock, poi collegamento a backend reale. |
| Backend | FastAPI in `backend/main.py` con router dedicato `backend/api/routes/protocollo_monitor.py`. | Route sottili, service layer applicativo, repository per Access. |
| Database | Microsoft Access configurato centralmente in `backend/core/config.py`. | Compatibilita attuale con Access, schema disegnato PostgreSQL-friendly. |
| Acquisizione Grisù | Runtime legacy in `Python/server_protocollo.py` e estensione in `Estensione/`. | Non modificare salvo richiesta esplicita; mantenere flusso acquisizione stabile. |
| File PDF protocollati | `backend/FileServer/YYYY/MM` e campo `T_Protocolli.PercorsoDocumentoProtocollato`. | Separare storage fisico da registrazione DB. |
| Procedimenti | Entita operativa introdotta con `T_Procedimenti` e tabelle workflow. | Procedimento come contenitore logico di protocolli, fasi, sottofasi e documenti. |
| Workflow sottofase | Ciclo interno fisso: REDIGI, REVISIONA, FIRMA, PROTOCOLLA, FINE. | Lettura read-only, validazione pura, poi scrittura controllata con backup. |

Flusso logico backend:

```text
FastAPI router
  -> DependencyContainer
      -> Service Layer
          -> Repository Layer
              -> Access oggi
              -> PostgreSQL domani
```

Flusso logico frontend:

```text
Vista Vue
  -> componente Vuetify
      -> procedimentoApi.js
          -> endpoint FastAPI
```

## 2. Strategie adottate

| Strategia | Applicazione concreta |
| --- | --- |
| Sviluppo step by step | Ogni avanzamento e stato isolato in step numerati, con vincoli espliciti e verifiche. |
| Backup Access obbligatorio | Ogni scrittura reale passa da `backend/core/access_backup.py`. Se il backup fallisce, la scrittura si ferma. |
| Separazione router/service/repository | Gli endpoint stanno nel router; le regole nei service; SQL e transazioni nei repository. |
| Read-only prima delle scritture | Procedimenti, workflow e sottofase documentale sono partiti in sola lettura prima di ogni write. |
| Test con fake repository | Le scritture sono state testate con fake repository/service prima del database reale. |
| Commit a milestone | Lo storico Git mostra commit per le milestone principali fino a Step 30L-15. |
| Configurazione centralizzata | Percorso Access e parametri applicativi stanno in `backend/core/config.py`. |
| No hardcoding in repository/service | I repository/service usano configurazione e container, non percorsi locali hardcoded. |
| Rollback transazionale | Le scritture workflow e documenti usano commit/rollback su Access. |
| UI progressiva | Workflow prima mock, poi read-only reale, poi azioni simulate, poi azioni backend reali. |
| Compatibilita Grisù | `Python/server_protocollo.py` resta escluso dalle modifiche salvo step mirati. |
| PostgreSQL-friendly | Chiavi surrogate, tabelle normalizzate, stati testuali stabili, relazioni logiche esplicite. |

## 3. Tabelle create o coinvolte

| Tabella | Scopo | Campi principali | Relazioni logiche | Stato |
| --- | --- | --- | --- | --- |
| `T_Protocolli` | Tabella storica dei protocolli acquisiti da Grisù/Vigilia. | `IDProtocollo`, `NumeroProtocollo`, `DataProtocollo`, `Modalita`, `ComandoMittente`, `Oggetto`, `PercorsoDocumentoProtocollato`, `DaLavorare`, `DataScadenza`, `TipologiaDocumento`. | Collegata logicamente a `T_ProcedimentoProtocolli.IDProtocollo`; usata da repository protocolli, documenti e metadata. | Gia usata in runtime. |
| `T_Procedimenti` | Contenitore logico-operativo di protocolli/documenti. | `IDProcedimento`, `CodiceProcedimento`, `Titolo`, `Descrizione`, `AziendaSoggetto`, `ComandoCompetenza`, `SettoreCompetenza`, `TipologiaProcedimento`, `StatoProcedimento`, `Priorita`, date operative, `Attivo`. | Padre di `T_ProcedimentoFasi`; collegata a `T_Protocolli` tramite ponte. | Gia usata da API e frontend. |
| `T_ProcedimentoProtocolli` | Ponte tra procedimento e protocollo. | `IDProcedimentoProtocollo`, `IDProcedimento`, `IDProtocollo`, `RuoloProtocollo`, `Principale`, `DataCollegamento`, `NoteCollegamento`. | `T_Procedimenti` <-> `T_Protocolli`; indice unico su procedimento/protocollo. | Gia usata per collegamento protocollo-procedimento. |
| `T_ProcedimentoFasi` | Fasi verticali del workflow procedimento. | `IDFase`, `IDProcedimento`, `CodiceFase`, `Titolo`, `Ordine`, `StatoFase`, `Responsabile`, `DataScadenza`, `DataAvvio`, `DataCompletamento`, `Obbligatoria`, `Bloccante`. | Figlia di `T_Procedimenti`; padre di `T_ProcedimentoSottofasi`. | Gia usata da API workflow procedimento e UI. |
| `T_ProcedimentoSottofasi` | Sottofasi operative dentro una fase. | `IDSottofase`, `IDFase`, `IDCatalogoSottofase`, `CodiceSottofase`, `Titolo`, `Ordine`, `StatoSottofase`, `Icona`, `Colore`, `Responsabile`, date operative, campi documentali Step 30L. | Figlia di `T_ProcedimentoFasi`; collegata a documenti e step operativi. | Gia usata da UI workflow e sottofase documentale. |
| `L_CatalogoSottofasi` | Catalogo riusabile per aggiungere sottofasi. | `IDCatalogoSottofase`, `CodiceSottofase`, `Titolo`, `Descrizione`, `Icona`, `Colore`, `Categoria`, `OrdineDefault`, `Attivo`. | Riferimento opzionale da `T_ProcedimentoSottofasi.IDCatalogoSottofase`. | Gia usata per tendina/avatar e dati reali. |
| `T_SottofaseDocumenti` | Storico versionato dei documenti collegati a una sottofase. | `IDDocumentoSottofase`, `IDSottofase`, `TipoDocumento`, `NomeFile`, `Estensione`, `PercorsoDocumento`, `MimeType`, `DimensioneBytes`, `HashFile`, `VersioneDocumento`, `DataCollegamento`, `UtenteCollegamento`, `Attivo`. | Figlia logica di `T_ProcedimentoSottofasi`; puo essere documento corrente della sottofase. | Gia usata in read-only, apertura documento e upload Word. |
| `T_SottofaseStepOperativi` | Storico degli step interni della sottofase documentale. | `IDStepSottofase`, `IDSottofase`, `CodiceStep`, `Ordine`, `StatoStep`, `DataAvvio`, `DataCompletamento`, `NoteStep`, `UtenteAssegnato`, `UtenteCompletamento`, `IDDocumentoSottofase`, `VersioneDocumento`. | Figlia logica di `T_ProcedimentoSottofasi`; storico REDIGI/FIRMA/etc. | Gia usata per workflow e azioni reali. |
| `T_SottofasePartecipanti` | Partecipanti assegnati a una sottofase o a uno step timeline. | `IDPartecipante`, `IDSottofase`, `IDStepOperativo`, `IDUtente`, `NomeVisualizzato`, `Email`, `Ruolo`, `StatoPartecipante`, `Ordine`, `ColoreAvatar`, `Iniziali`, date, note, `Attivo`. | Figlia logica di `T_ProcedimentoSottofasi`; `IDStepOperativo` opzionale collega il partecipante a uno step in `T_SottofaseStepOperativi`. | Creata Step 30L-22, estesa Step 30L-27 con backup. |
| `T_Documenti` | Tabella documentale legacy/predisposta. | Dipende dallo schema Access esistente; usata in modo prudente da `DocumentoRepository`. | Relazione indiretta con protocolli tramite path documento. | Coinvolta ma non centrale nel nuovo workflow. |

## 4. Campi aggiunti o usati

| Tabella | Campo | Significato operativo | Uso frontend/backend | Impatto PostgreSQL |
| --- | --- | --- | --- | --- |
| `T_ProcedimentoSottofasi` | `StepCorrente` | Step documentale corrente: `REDIGI`, `REVISIONA`, `FIRMA`, `PROTOCOLLA`, `FINE`. | Backend calcola workflow e validazioni; frontend evidenzia step attivo. | Diventera `varchar(50)` con possibile `CHECK` o lookup. |
| `T_ProcedimentoSottofasi` | `TestoOperatore` | Testo libero inserito durante un'azione workflow. | Textarea read-only e payload azioni workflow. | `text`; audit futuro potra storicizzarlo per evento. |
| `T_ProcedimentoSottofasi` | `HaDocumentoCollegato` | Flag rapido che indica presenza documento collegato. | Chip "Documento presente/assente"; aggiornato da upload Word. | Campo denormalizzato sostituibile con vista o query aggregata. |
| `T_ProcedimentoSottofasi` | `IDDocumentoCorrente` | Riferimento al documento attivo/corrente. | Card documento corrente, pulsante Visualizza, upload Word. | Foreign key verso `sottofase_documenti`. |
| `T_ProcedimentoSottofasi` | `DataUltimaAzione` | Timestamp ultima azione significativa. | Stato documentale e workflow. | `timestamptz`; utile per audit e ordinamenti. |
| `T_ProcedimentoSottofasi` | `UtenteUltimaAzione` | Operatore dell'ultima azione. | UI mostra operatore; oggi valore provvisorio. | Diventera FK verso utenti quando ci sara login reale. |
| `T_ProcedimentoSottofasi` | `VersioneDocumento` | Cache della versione corrente. | UI mostra `vN`; aggiornato da upload Word. | Campo cache, fonte autorevole futura resta tabella documenti. |
| `T_ProcedimentoSottofasi` | `StatoSottofase` | Stato operativo della sottofase. | Timeline, chip stato, chiusura sottofase. | `varchar(50)` con enum/check. |
| `T_ProcedimentoSottofasi` | `DataCompletamento` | Data completamento sottofase. | Usata per considerare FINE completato. | `timestamptz`; utile per metriche. |
| `T_SottofaseDocumenti` | `PercorsoDocumento` | Path fisico del file Word/PDF/allegato. | Apertura documento e storico versioni. | In PostgreSQL resta metadato; file storage resta esterno. |
| `T_SottofaseDocumenti` | `HashFile` | Hash del file al collegamento. | Calcolato in upload Word; utile per integrita. | `varchar(128)`; possibile deduplica futura. |
| `T_SottofaseStepOperativi` | `CodiceStep` | Step completato o registrato nello storico. | Backend legge completamenti; UI mostra storico operativo. | `varchar(50)` con enum/check. |
| `T_SottofaseStepOperativi` | `StatoStep` | Stato dello step, oggi soprattutto `COMPLETATO`. | Calcolo completamento workflow. | `varchar(50)` con enum/check. |
| `T_Protocolli` | `PercorsoDocumentoProtocollato` | Path PDF protocollato. | Endpoint PDF, metadata `pdf_disponibile`, viewer Vue. | Resterà path/metadato documentale o relazione documenti. |

## 5. Endpoint backend

| Metodo | Endpoint | Scopo | Tipo | Repository/service coinvolti | Stato |
| --- | --- | --- | --- | --- | --- |
| `GET` | `/protocollo-monitor/protocolli` | Elenco protocolli acquisiti. | Read-only | `ProtocolloService`, `ProtocolloRepository`. | Attivo. |
| `GET` | `/protocollo-monitor/protocolli/{id_protocollo}` | Dettaglio protocollo con relazioni. | Read-only | `ProtocolloService`, `ProtocolloRepository`. | Attivo. |
| `GET` | `/protocollo-monitor/protocolli/{id_protocollo}/metadata` | Metadati protocollo e disponibilita PDF. | Read-only | `MetadataService`, `MetadataRepository`, `DocumentPathService`. | Attivo. |
| `GET` | `/protocollo-monitor/protocolli/{id_protocollo}/pdf` | Visualizzazione PDF inline. | Read-only/filesystem | `DocumentoService`, `DocumentoRepository`, `DocumentPathService`. | Attivo. |
| `GET` | `/protocollo-monitor/protocolli/{id_protocollo}/apri-pdf` | Apertura locale PDF su Windows. | Read-only con side-effect locale | `DocumentoService`, `DocumentPathService`, `subprocess`. | Attivo, Windows-specific. |
| `GET` | `/protocollo-monitor/procedimenti` | Elenco procedimenti. | Read-only | `ProcedimentoService`, `ProcedimentoRepository`. | Attivo. |
| `GET` | `/protocollo-monitor/procedimenti/{id_procedimento}` | Dettaglio procedimento. | Read-only | `ProcedimentoService`, `ProcedimentoRepository`. | Attivo. |
| `GET` | `/protocollo-monitor/procedimenti/{id_procedimento}/protocolli` | Protocolli collegati a procedimento. | Read-only | `ProcedimentoService`, `ProcedimentoRepository`. | Attivo. |
| `GET` | `/protocollo-monitor/procedimenti/{id_procedimento}/protocolli/count` | Conteggio protocolli collegati. | Read-only | `ProcedimentoService`, `ProcedimentoRepository`. | Attivo. |
| `GET` | `/protocollo-monitor/protocolli/{id_protocollo}/procedimenti` | Procedimenti collegati a protocollo. | Read-only | `ProcedimentoService`, `ProcedimentoRepository`. | Attivo. |
| `POST` | `/protocollo-monitor/protocolli/{id_protocollo}/procedimenti/{id_procedimento}` | Collega protocollo a procedimento. | Scrittura minima | `ProcedimentoService`, `ProcedimentoRepository`. | Attivo con 404/409. |
| `GET` | `/protocollo-monitor/procedimenti/{id_procedimento}/fasi` | Fasi workflow procedimento. | Read-only | `WorkflowProcedimentoService`, `WorkflowProcedimentoRepository`. | Attivo. |
| `GET` | `/protocollo-monitor/procedimenti/fasi/{id_fase}` | Dettaglio fase. | Read-only | `WorkflowProcedimentoService`, `WorkflowProcedimentoRepository`. | Attivo. |
| `GET` | `/protocollo-monitor/procedimenti/fasi/{id_fase}/sottofasi` | Sottofasi di una fase. | Read-only | `WorkflowProcedimentoService`, `WorkflowProcedimentoRepository`. | Attivo. |
| `GET` | `/protocollo-monitor/catalogo-sottofasi` | Catalogo sottofasi per tendina/avatar. | Read-only | `WorkflowProcedimentoService`, `WorkflowProcedimentoRepository`. | Attivo. |
| `GET` | `/protocollo-monitor/sottofasi/{id_sottofase}/documentale` | Quadro documentale sottofase. | Read-only | `SottofaseDocumentaleService`, `SottofaseDocumentaleRepository`. | Attivo. |
| `GET` | `/protocollo-monitor/sottofasi/{id_sottofase}/documenti` | Storico documenti sottofase. | Read-only | `SottofaseDocumentaleService`, `SottofaseDocumentaleRepository`. | Attivo. |
| `POST` | `/protocollo-monitor/sottofasi/{id_sottofase}/documenti` | Upload Word versionato in REDIGI e REVISIONA. | Scrittura controllata | `SottofaseDocumentUploadService`, `SottofaseDocumentUploadRepository`, backup Access. | Attivo Step 30L-16. |
| `GET` | `/protocollo-monitor/sottofasi/{id_sottofase}/step-operativi` | Step operativi storici. | Read-only | `SottofaseDocumentaleService`, `SottofaseDocumentaleRepository`. | Attivo. |
| `GET` | `/protocollo-monitor/sottofase-documenti/{id_documento}/apri` | Apre/serve documento collegato Word/PDF/storico. | Read-only/filesystem | `SottofaseDocumentaleService`, `DocumentPathService`, `FileResponse`. | Attivo Step 30L-17, invariato lato backend. |
| `GET` | `/protocollo-monitor/sottofase-documenti/{id_documento}/scarica` | Scarica documento collegato Word/PDF/storico con `Content-Disposition: attachment`. | Read-only/filesystem | `SottofaseDocumentaleService`, `DocumentPathService`, `FileResponse`. | Attivo Step 30L-18. |
| `GET` | `/protocollo-monitor/sottofasi/{id_sottofase}/partecipanti` | Elenco partecipanti attivi collegati alla sottofase. | Read-only | `SottofasePartecipantiService`, `SottofasePartecipantiRepository`. | Attivo Step 30L-22. |
| `POST` | `/protocollo-monitor/sottofasi/{id_sottofase}/partecipanti` | Inserisce un partecipante sottofase con backup Access e validazioni. | Scrittura controllata | `SottofasePartecipantiService`, `SottofasePartecipantiRepository`, backup Access. | Attivo Step 30L-22. |
| `GET` | `/protocollo-monitor/sottofasi/{id_sottofase}/step-operativi/{id_step}/partecipanti` | Elenco partecipanti attivi collegati a uno specifico step timeline. | Read-only | `SottofasePartecipantiService`, `SottofasePartecipantiRepository`. | Attivo Step 30L-27. |
| `GET` | `/protocollo-monitor/sottofasi/{id_sottofase}/workflow` | Workflow operativo REDIGI/FINE. | Read-only | `SottofaseWorkflowService`, `SottofaseDocumentaleService`. | Attivo. |
| `POST` | `/protocollo-monitor/sottofasi/{id_sottofase}/workflow/azioni` | Avanza workflow sottofase. | Scrittura controllata | `SottofaseWorkflowCommandService`, `SottofaseWorkflowActionRepository`, backup Access. | Attivo. |
| `POST` | `http://127.0.0.1:8020/open-word` | Helper locale separato per aprire `.docx` con Word da `idDocumento`. | Read-only locale/filesystem | `Python/open_word_helper.py`, Access read-only, whitelist `DocumentiWorkflow`. | Attivo Step 30L-19, fuori dal backend principale. |
| `GET` | `http://127.0.0.1:8020/health` | Health check helper locale Apri con Word. | Read-only locale | `Python/open_word_helper.py`. | Attivo Step 30L-20. |

## 6. Componenti frontend

| Componente/view | Scopo | Controlli inseriti | Endpoint consumati | Eventi | Stato |
| --- | --- | --- | --- | --- | --- |
| `ProcedimentiView.vue` | Elenco procedimenti. | Data table, ricerca libera, filtri stato/priorita, click dettaglio. | `GET /procedimenti`, count protocolli. | Navigazione verso dettaglio. | Attivo read-only. |
| `ProcedimentoDettaglioView.vue` | Dettaglio procedimento, fasi, sottofasi e protocolli. | Pannello sinistro fasi, timeline, dettaglio fase, sottofasi, pulsante aggiungi fase locale, selezione sottofase. | Procedimento, protocolli, fasi, sottofasi, catalogo. | Ascolta `workflow-aggiornato`, ricarica sottofase/documentale. | Attivo. |
| `SottofaseDocumentaleCard.vue` | Stato documentale di una sottofase. | Chip documento presente, card documento corrente, storico documenti, step operativi, azioni separate Apri/Scarica/Apri con Word tramite helper locale. | `GET /documentale`, `GET /sottofase-documenti/{id}/apri`, `GET /sottofase-documenti/{id}/scarica`, `POST helper /open-word`. | Nessun evento principale; si aggiorna via remount/key padre. | Attivo Step 30L-19. |
| `WorkflowSottofaseCard.vue` | Workflow operativo sottofase e azioni. | Progress bar, step verticali, azioni disponibili, dialog conferma, textarea, upload Word REDIGI/REVISIONA. | `GET /workflow`, `POST /workflow/azioni`, `POST /documenti`. | Emette `workflow-aggiornato`. | Attivo. |
| `procedimentoApi.js` | Client API frontend. | Helper fetch JSON/blob, FormData per upload Word. | Tutti gli endpoint procedimento/workflow/documentale. | Non emette eventi; usato dai componenti. | Attivo. |
| `NotaProtocolloView.vue` | Dettaglio protocollo e collegamento procedimenti. | Card procedimenti collegati, dialog collegamento, PDF. | Protocolli, procedimenti collegati, POST link. | Refresh dati dopo link. | Attivo. |

## 7. Controlli UI aggiunti

Controlli gia introdotti:

- stepper/timeline verticale fasi procedimento;
- colonna fissa per cerchi numerati e linea verticale centrata;
- pannello "Fasi del procedimento";
- pulsante "Aggiungi fase" nella testata fasi;
- sottofasi orizzontali con avatar;
- catalogo sottofasi da API reale;
- stato documentale con `v-chip`;
- card documento corrente;
- storico documenti;
- step operativi;
- workflow operativo REDIGI/FINE;
- azioni disponibili;
- dialog conferma azione;
- textarea testo operatore;
- skeleton loader;
- `v-alert` per errori, info e successo;
- `v-chip` per stati e percentuali;
- `v-progress-linear` per avanzamento workflow;
- pulsanti Visualizza, Apri, Conferma, Carica documento;
- upload `.docx` con `v-file-input`, preview nome/dimensione e limite 50 MB in REDIGI e REVISIONA.
- apertura documento corrente e versioni storiche con pulsanti dedicati Word/PDF, tooltip, loading anti doppio click e alert errori.
- distinzione tra Apri nel browser, Scarica file e pulsante futuro Apri con Word disabilitato per `.docx`.
- helper locale Windows `open_word_helper.py` per Apri con Word, separato dal backend principale e vincolato a `.docx` dentro `DocumentiWorkflow`.
- batch locale `Avvia_ProtocolloMonitor.bat` per avviare FastAPI, frontend, Flask Grisu e helper Word in finestre separate.

## 8. Workflow operativo sottofase

Workflow standard:

```text
REDIGI -> REVISIONA -> FIRMA -> PROTOCOLLA -> FINE
```

| Step | Quando e attivo | Quando e completato | Azione che lo avanza | Storico inserito | Campo aggiornato |
| --- | --- | --- | --- | --- | --- |
| `REDIGI` | Se `StepCorrente` e `REDIGI` o se non ci sono step completati e nessun altro step attivo. | Se storico REDIGI completato o `StepCorrente` e successivo. | `AVVIA_REDAZIONE`. | Record `T_SottofaseStepOperativi` con `CodiceStep=REDIGI`, `StatoStep=COMPLETATO`. | `StepCorrente=REVISIONA`, `TestoOperatore`, `DataUltimaAzione`, `UtenteUltimaAzione`. |
| `REVISIONA` | Se `StepCorrente=REVISIONA`. | Se storico REVISIONA completato o `StepCorrente` successivo. | `INVIA_REVISIONE`. | Record con `CodiceStep=REVISIONA`. | `StepCorrente=FIRMA` e campi ultima azione. |
| `FIRMA` | Se `StepCorrente=FIRMA`, anche senza documento corrente. | Se storico FIRMA completato o `StepCorrente` successivo. | `SEGNA_FIRMATO`. | Record con `CodiceStep=FIRMA`. | `StepCorrente=PROTOCOLLA` e campi ultima azione. |
| `PROTOCOLLA` | Se `StepCorrente=PROTOCOLLA`. | Se storico PROTOCOLLA completato o `StepCorrente` successivo. | `SEGNA_PROTOCOLLATO`. | Record con `CodiceStep=PROTOCOLLA`. | `StepCorrente=FINE` e campi ultima azione. |
| `FINE` | Se `StepCorrente=FINE`. | Se sottofase completata o storico FINE completato. | `CHIUDI_SOTTOFASE`. | Record con `CodiceStep=FINE`. | `StatoSottofase=COMPLETATA`, `DataCompletamento`, `StepCorrente=FINE`. |

Regole importanti:

- non si salta uno step;
- non si torna indietro;
- la chiusura e ammessa solo quando lo step attivo e `FINE`;
- il documento corrente non blocca piu `FIRMA` se `StepCorrente=FIRMA`;
- l'assenza di documento puo essere mostrata come informazione, non come blocco assoluto.

## 9. Strategie documentali

| Concetto | Strategia |
| --- | --- |
| Documento corrente | `T_ProcedimentoSottofasi.IDDocumentoCorrente` punta al documento corrente. |
| Storico versioni | Ogni upload crea record in `T_SottofaseDocumenti` con `VersioneDocumento` progressiva. |
| Path fisico | I file Word sono salvati in `DocumentiWorkflow/IDSottofase/Vnnn/Documento_IDSottofase_Vnnn.docx`. |
| Apertura documento | Endpoint `GET /protocollo-monitor/sottofase-documenti/{id_documento}/apri` restituisce file con `FileResponse`. |
| `documentoCorrenteMancante` | Il workflow puo segnalarlo per informazione; non blocca piu la firma. |
| Rapporto file/workflow | Il file e tracciato separatamente dal workflow; il workflow registra avanzamenti operativi. |
| Versionamento | Non si sovrascrive: V001, V002, V003. |
| Integrita | Upload calcola hash SHA-256 e dimensione file. |
| Rollback file | Se il DB fallisce dopo il salvataggio file, il service rimuove il file appena creato. |
| Revisione Word | Durante REVISIONA lo stesso endpoint crea V002/V003, aggiorna il documento corrente e mantiene V001 nello storico `T_SottofaseDocumenti`. |

## 10. Backup e rollback

| Tema | Regola |
| --- | --- |
| Dove | Cartella `Backup` accanto al database Access configurato. |
| Nome | `ProtocolloMonitor_BACKUP_YYYYMMDD_HHMMSS.accdb`. |
| Quando | Prima di ogni scrittura reale su Access: workflow azioni e upload documento Word. |
| Verifica | Esistenza file, dimensione maggiore di zero, dimensione uguale al sorgente. |
| Lock | Se esiste `.laccdb`, il backup viene considerato non sicuro e la scrittura si ferma. |
| Se backup fallisce | Nessuna scrittura deve partire. |
| Rollback DB | Repository di scrittura usa `commit()` solo dopo tutte le query; in errore usa `rollback()`. |
| Rollback file | Upload Word rimuove il file salvato se la registrazione Access fallisce. |
| Stato lock dopo test | Nei test reali noti non e rimasto lock `.laccdb`. |

Componenti coinvolti:

- `backend/core/access_backup.py`;
- `SottofaseWorkflowCommandService`;
- `SottofaseWorkflowActionRepository`;
- `SottofaseDocumentUploadService`;
- `SottofaseDocumentUploadRepository`.

## 11. Test eseguiti

Verifiche ricorrenti:

| Verifica | Stato noto |
| --- | --- |
| `python -m py_compile ...` | Eseguito sui moduli backend modificati negli step. |
| `python -m pytest tests` | Ultimo risultato noto Step 30L-15: `182 passed`. |
| `npm.cmd run build` | Build frontend eseguita con successo negli step frontend recenti. |
| Test endpoint reali | Eseguiti per workflow azioni e upload documento Word. |
| Test sottofase 5 | Workflow reale portato fino a chiusura in Step 30L-14. |
| Workflow completo | `FIRMA -> PROTOCOLLA -> FINE`, percentuale finale 100%. |
| Upload Word reale | Step 30L-15: upload su sottofase reale in REDIGI, backup e documento V001 creati. |
| Rollback | Test fake repository/service coprono rollback DB e rimozione file su errore. |

Test automatici principali:

- `test_access_backup.py`;
- `test_sottofase_workflow_action_service.py`;
- `test_sottofase_workflow_command_service.py`;
- `test_sottofase_workflow_action_repository.py`;
- `test_sottofase_workflow_endpoint.py`;
- `test_sottofase_documentale_*`;
- `test_sottofase_document_upload_service.py`;
- `test_sottofase_document_upload_repository.py`;
- test procedimenti, workflow procedimento, metadata, PDF, storage.

## 12. Milestone completate

| Step | Titolo | Cosa e stato fatto | File principali | Stato | Commit rilevato |
| --- | --- | --- | --- | --- | --- |
| Step 30L-4 | Applicazione schema sottofase documentale | Applicati campi documentali e tabelle documentali su Access con backup. | Documentazione/script DB; database reale. | Completato. | Non rilevato direttamente nel log recente. |
| Step 30L-5 | Backend read-only sottofase documentale | Repository/service/API per quadro documentale, documenti, step operativi. | `sottofase_documentale_repository.py`, `sottofase_documentale_service.py`, router, test. | Completato. | `30b845e`. |
| Step 30L-6 | Frontend lettura sottofase documentale | Card documentale con documento corrente, storico, step operativi. | `SottofaseDocumentaleCard.vue`, `procedimentoApi.js`, vista dettaglio. | Completato. | `f7a973f`. |
| Step 30L-7 | Apertura documenti sottofase | Endpoint apertura documento e pulsanti Visualizza/Apri. | Router, service documentale, `SottofaseDocumentaleCard.vue`. | Completato. | `ab54494`. |
| Step 30L-8 | Workflow operativo sottofase read-only | Endpoint workflow e componente workflow con progress bar. | `sottofase_workflow_service.py`, `WorkflowSottofaseCard.vue`, test. | Completato. | `204ddbc`. |
| Step 30L-8 bis | UI workflow e stepper | Ripristinato pulsante Aggiungi fase e allineata linea stepper. | `ProcedimentoDettaglioView.vue`. | Completato. | `3405ffb`. |
| Step 30L-9 | Azioni workflow simulate | Pulsanti azione e dialog senza scritture. | `WorkflowSottofaseCard.vue`. | Completato. | `a355912`. |
| Step 30L-10 | Contratto azioni workflow | Schema payload, enum azioni, validazione pura, test. | `sottofase_workflow.py`, `sottofase_workflow_action_service.py`, test. | Completato. | `e5dc349`. |
| Step 30L-11 | Scrittura controllata workflow | POST reale con backup, update sottofase, insert storico, rollback. | `sottofase_workflow_command_service.py`, `sottofase_workflow_action_repository.py`, router, test. | Completato. | `337b91a`, `bfb378f`. |
| Step 30L-12 | Frontend azioni reali | Collegata UI al POST reale, refresh dopo successo. | `WorkflowSottofaseCard.vue`, `procedimentoApi.js`, vista dettaglio. | Completato. | `ccd38f0`. |
| Step 30L-13 | Regole FIRMA/documento corrente | FIRMA non bloccata da assenza documento corrente. | Workflow service, action service, test. | Completato. | `01e2d53`. |
| Step 30L-14 | Prosecuzione reale fino a chiusura | Test reale sequenza `SEGNA_FIRMATO`, `SEGNA_PROTOCOLLATO`, `CHIUDI_SOTTOFASE` su sottofase 5. | Endpoint esistente e database reale. | Completato operativamente. | Non rilevato come commit dedicato. |
| Step 30L-15 | Documento Word reale REDIGI | Upload `.docx`, V001/V002, backup, insert documento, update documento corrente, UI upload. | `sottofase_document_upload_*`, router, `WorkflowSottofaseCard.vue`, `procedimentoApi.js`, test. | Completato. | `38dfada`. |
| Step 30L-16 | Revisione documento Word | Upload `.docx` ammesso anche in REVISIONA, generazione V002/V003, storico versioni conservato, documento corrente aggiornato, UI revisione. | `sottofase_document_upload_service.py`, router, `WorkflowSottofaseCard.vue`, test upload. | Completato. | Da commit. |
| Step 30L-17 | Apertura documento Word corrente e storico | Migliorata UI apertura documento corrente e versioni storiche, label Word/PDF, tooltip, loading, gestione errori 404/500 e popup bloccato usando endpoint esistente. | `SottofaseDocumentaleCard.vue`, `procedimentoApi.js`, roadmap. | Completato. | Da commit. |
| Step 30L-18 | Distinzione Apri/Scarica/Apri con Word | Aggiunto endpoint read-only `/scarica`, UI con azioni separate per documento corrente e storico, download attachment, pulsante Apri con Word disabilitato/informativo. | Router, `SottofaseDocumentaleCard.vue`, `procedimentoApi.js`, test endpoint, roadmap. | Completato. | Da commit. |
| Step 30L-19 | Helper locale Windows Apri con Word | Creato helper separato `POST /open-word` su `127.0.0.1:8020`, recupero path da `idDocumento`, whitelist `DocumentiWorkflow`, solo `.docx`, UI collegata e gestione helper non avviato. | `Python/open_word_helper.py`, `SottofaseDocumentaleCard.vue`, `procedimentoApi.js`, test helper, roadmap. | Completato. | Da commit. |
| Step 30L-20 | Avvio automatico helper locali | Aggiornato batch locale per avviare backend FastAPI, frontend Vue, server Flask Grisu e helper Apri con Word; aggiunto health check helper. | `Python/Avvia_ProtocolloMonitor.bat`, `Python/open_word_helper.py`, roadmap. | Completato. | Da commit. |
| Step 30L-22 | Partecipanti sottofase | Creata tabella `T_SottofasePartecipanti`, repository/service/schema Pydantic, endpoint GET/POST, validazioni e test. | `sottofase_partecipanti_*`, router, dependency container, test, roadmap. | Completato. | Da commit. |
| Step 30L-27 | Partecipanti collegati allo step | Estesa `T_SottofasePartecipanti` con `IDStepOperativo`, validazioni step/sottofase/ruolo, endpoint GET per partecipanti step e test. | `sottofase_partecipanti_*`, router, test, roadmap. | Completato. | Da commit. |

## 13. Decisioni architetturali importanti

1. Access resta solo la fase iniziale operativa.
2. Lo schema e progettato PostgreSQL-friendly, con relazioni normalizzate e chiavi surrogate.
3. `T_Protocolli` resta stabile: le nuove relazioni usano tabelle ponte o tabelle figlie.
4. Procedimento, documenti e workflow sono domini separati.
5. Nessuna scrittura reale avviene senza backup Access.
6. Nessuna modifica a `Python/server_protocollo.py` salvo richiesta esplicita.
7. Frontend progressivo: lettura, simulazione, azione reale.
8. Backend progressivo: read-only, contratto, validazione pura, scrittura controllata.
9. Il documento fisico non e il workflow: il file viene versionato, il workflow registra l'avanzamento.
10. `FIRMA` non dipende piu obbligatoriamente da documento corrente se `StepCorrente=FIRMA`.
11. L'utente reale non e ancora integrato: oggi viene usato un operatore provvisorio.
12. Il logging strutturato e predisposto; audit applicativo completo resta futuro.

## Step 30L-21A – Rifondazione modello sottofase

Questo step e esclusivamente architetturale. Non introduce modifiche a codice,
database, schema Access, endpoint o frontend.

### Modello precedente

Il modello implementato negli step precedenti considera la sottofase come
contenitore di un workflow interno fisso:

```text
FASE
  -> SOTTOFASE
      -> WORKFLOW
          -> REDIGI
          -> REVISIONA
          -> FIRMA
          -> PROTOCOLLA
          -> FINE
```

Questo modello e tecnicamente funzionante ed e stato testato end-to-end:
workflow read-only, azioni reali, upload Word versionato, apertura/scarico del
documento, helper Word, backup Access e rollback sono stati verificati negli
step precedenti.

### Criticita emerse

La criticita concettuale principale e che `REDIGI`, `REVISIONA`, `FIRMA`,
`PROTOCOLLA` e `FINE` non rappresentano step interni di una singola sottofase:
sono sottofasi vere e proprie attraversate dal documento.

Nel modello precedente la sottofase ha due livelli operativi sovrapposti:

- lo stato della sottofase;
- lo stato del workflow interno della sottofase tramite `StepCorrente` e
  `T_SottofaseStepOperativi`.

Questa sovrapposizione rende meno naturale rappresentare partecipanti,
funzionalita specifiche, allegati, stati visuali e azioni diverse per ogni
sottofase.

### Nuovo modello concettuale

Il documento diventa il protagonista del procedimento. La fase contiene una
sequenza di sottofasi operative attraversate dal documento:

```text
FASE
  -> REDIGI
  -> REVISIONA
  -> FIRMA
  -> PROTOCOLLA
  -> FINE
```

Il percorso logico diventa:

```text
Documento
  -> REDIGI
  -> REVISIONA
  -> FIRMA
  -> PROTOCOLLA
  -> FINE
```

Ogni sottofase puo avere:

- stato;
- nota operatore;
- documento principale;
- storico versioni del documento principale;
- allegati del documento principale;
- partecipanti;
- azioni operative;
- funzionalita specifiche.

Il nuovo modello logico della sottofase e:

```text
SOTTOFASE
  -> Stato
  -> Nota operatore
  -> Documento principale
  -> Storico versioni
  -> Allegati
  -> Partecipanti
  -> Funzionalita specifiche
```

### Partecipanti sottofase

Il modello introduce il concetto architetturale di `PartecipanteSottofase`.

Campi concettuali:

- utente;
- ruolo;
- stato;
- data azione;
- note.

Ruoli previsti:

- `REVISORE`;
- `FIRMATARIO`;
- `APPROVATORE`;
- `OPERATORE`;
- `OSSERVATORE`.

Le sottofasi possono mostrare i partecipanti tramite avatar a ventaglio. Per
esempio:

- `REVISIONA` mostra i revisori;
- `FIRMA` mostra i firmatari;
- `APPROVAZIONE` mostra gli approvatori.

I partecipanti influenzano visivamente lo stato della sottofase:

- avatar grigio: azione non eseguita;
- avatar colorato: azione completata;
- avatar rosso: respinto;
- avatar giallo: richiesta integrazione.

### Funzionalita specifiche

Le sottofasi non sono tutte uguali e non devono essere forzate dentro lo stesso
workflow interno.

Esempi:

- `REVISIONA`: revisori assegnati, commenti, esito revisione;
- `FIRMA`: firmatari, data firma, stato firma;
- `PROTOCOLLA`: numero protocollo, data protocollo.

### Principi guida

1. Il documento e il protagonista del procedimento.
2. `REDIGI`, `REVISIONA`, `FIRMA`, `PROTOCOLLA` e `FINE` sono sottofasi, non
   step interni.
3. La fase ordina sottofasi attraversate dal documento.
4. La sottofase e il punto in cui convergono stato, documento, partecipanti e
   funzionalita specifiche.
5. Il documento principale resta versionato e puo avere allegati.
6. La migrazione dal workflow interno al nuovo modello deve essere graduale e
   compatibile con quanto gia funziona.

### Cosa si conserva

Restano validi e da preservare:

- upload Word;
- versionamento;
- documento corrente;
- storico versioni;
- apertura/scarico documento;
- helper Word;
- backup;
- rollback;
- pannello documentale.

### Cosa va rivalutato

Vanno rivalutati alla luce del nuovo modello:

- `WorkflowSottofaseCard.vue`;
- `StepCorrente`;
- `T_SottofaseStepOperativi`;
- workflow interno delle sottofasi;
- azione `AVVIA_REDAZIONE`;
- azione `INVIA_REVISIONE`;
- azione `SEGNA_FIRMATO`;
- azione `SEGNA_PROTOCOLLATO`;
- azione `CHIUDI_SOTTOFASE`.

### Rischi di migrazione

- Dati gia scritti su `StepCorrente` e `T_SottofaseStepOperativi` da mappare
  senza perdita informativa.
- Endpoint e componenti frontend oggi coerenti con il workflow interno da
  ricondurre progressivamente al modello di sottofasi reali.
- Azioni esistenti da reinterpretare come transizioni tra sottofasi o azioni
  specifiche della singola sottofase.
- Storico documentale da mantenere stabile durante la migrazione.
- Necessita di non confondere firma operativa, firma digitale reale e
  protocollazione effettiva.

## Step 30L-21B – Analisi impatto sul codice esistente

Questo step e di sola analisi tecnica. Non modifica codice, database, schema
Access, endpoint o frontend.

### Sintesi impatto

La ricognizione conferma che la parte documentale e il contenitore
fase/sottofase sono riutilizzabili. La parte da rifondare e il significato del
workflow interno: `REDIGI`, `REVISIONA`, `FIRMA`, `PROTOCOLLA` e `FINE` non
devono piu essere considerati obbligatoriamente step interni di una sottofase,
ma possono diventare sottofasi reali o tipi di sottofase.

### Backend

| File | Ruolo attuale | Conservare | Rinominare | Semplificare | Dismettere | Impatto nuova architettura |
| --- | --- | --- | --- | --- | --- | --- |
| `backend/api/routes/protocollo_monitor.py` | Espone endpoint procedimenti, fasi, sottofasi, documentale, workflow, upload e apertura/scarico documenti. | Si, come router sottile. | Non subito. | Si, quando workflow e azioni saranno separati dal concetto di sottofase. | No. | Gli endpoint documentali restano validi; gli endpoint `/workflow` e `/workflow/azioni` vanno reinterpretati o affiancati da endpoint per azioni specifiche di sottofase. |
| `backend/services/sottofase_workflow_service.py` | Costruisce workflow fisso REDIGI/REVISIONA/FIRMA/PROTOCOLLA/FINE partendo dal quadro documentale e da `StepCorrente`. | Solo temporaneamente. | Probabile: verso service di compatibilita/mapping. | Si. | Non subito. | E il punto piu legato al vecchio modello; potra diventare adattatore legacy per leggere lo stato storico durante la migrazione. |
| `backend/services/sottofase_workflow_action_service.py` | Valida azioni fisse e sequenza lineare senza side effect. | Parzialmente. | Si, se trasformato in validatore di azioni sottofase. | Si. | Possibile dopo migrazione. | Le regole anti-salto e anti-ritorno sono utili come idea, ma le azioni devono dipendere dal tipo di sottofase e dai partecipanti. |
| `backend/services/sottofase_workflow_command_service.py` | Coordina lettura workflow, validazione, backup Access, scrittura transazionale e rilettura workflow. | La struttura transazionale si conserva. | Si, verso command service azioni sottofase. | Si. | No, se riusato come pattern. | Deve smettere di comandare una sequenza fissa e diventare orchestratore di azioni operative della sottofase. |
| `backend/services/sottofase_documentale_service.py` | Compone quadro documentale read-only: sottofase, documento corrente, documenti, step operativi. | Si. | Forse: da documentale sottofase a quadro sottofase. | Si, separando step operativi legacy. | No. | E coerente col nuovo modello: stato, nota, documento principale e storico restano centrali. |
| `backend/services/sottofase_document_upload_service.py` | Valida `.docx`, crea backup, salva versione fisica, registra documento e aggiorna documento corrente; oggi consente upload solo con step REDIGI/REVISIONA attivo. | Si. | Non necessario subito. | Si, rimuovendo dipendenza diretta dal workflow fisso. | No. | Il versionamento resta valido; la regola di abilitazione deve dipendere dal tipo/stato sottofase, non dallo step attivo. |
| `backend/repositories/sottofase_document_upload_repository.py` | Inserisce record in `T_SottofaseDocumenti` e aggiorna `T_ProcedimentoSottofasi.IDDocumentoCorrente`, `VersioneDocumento`, flag e ultima azione. | Si. | No. | Poco. | No. | Molto compatibile: rappresenta documento principale/versioni. In futuro andra esteso o affiancato per allegati. |
| `backend/repositories/sottofase_documentale_repository.py` | Legge campi sottofase, documenti e step operativi. | Si. | Non subito. | Si, isolando lettura step operativi come storico legacy. | No. | La lettura di `T_ProcedimentoSottofasi` e `T_SottofaseDocumenti` resta centrale; `T_SottofaseStepOperativi` diventa storico/mapping. |
| `backend/repositories/sottofase_workflow_action_repository.py` | Aggiorna `StepCorrente`, `TestoOperatore`, ultima azione, eventuale completamento sottofase e inserisce record in `T_SottofaseStepOperativi`. | Solo per compatibilita. | Si, se reinterpretato come repository storico azioni. | Si. | Possibile a fine migrazione. | Oggi e accoppiato al vecchio workflow; le scritture future dovrebbero agire su stato sottofase, partecipanti e azioni specifiche. |
| `backend/core/dependency_container.py` | Compone repository e service in modo lazy. | Si. | No. | Si, rimuovendo servizi legacy quando non servono. | No. | Resta il punto corretto per sostituire service workflow con service sottofase/azioni/partecipanti. |
| `backend/schemas/sottofase_workflow.py` | Definisce enum azioni fisse e payload azione workflow. | Temporaneamente. | Si, verso schema azioni sottofase. | Si. | Possibile. | Le azioni fisse vanno reinterpretate: alcune diventano transizioni tra sottofasi, altre azioni specifiche del tipo di sottofase. |

### Frontend

| File | Ruolo attuale | Parti utili | Parti da rivalutare | Parti da separare | Impatto UI futura |
| --- | --- | --- | --- | --- | --- |
| `frontend/src/views/ProcedimentoDettaglioView.vue` | Mostra procedimento, fasi, sottofasi, dettaglio sottofase, card documentale e card workflow. | Layout fase/sottofase, selezione sottofase, avatar semplice, caricamento fasi/sottofasi, refresh dopo evento. | Linguaggio "workflow", blocchi locali di aggiunta/eliminazione, completamento fase basato solo su sottofasi completate. | Pannello sottofase, timeline fase, area documentale, area azioni. | Diventa la vista naturale del nuovo modello: la sequenza REDIGI/FIRMA/etc. puo essere visualizzata come sottofasi della fase. |
| `frontend/src/components/procedimenti/WorkflowSottofaseCard.vue` | Mostra progress bar, step interni, azioni fisse, dialog conferma e upload Word REDIGI/REVISIONA. | UI dialog azione, gestione errori, loading, emit refresh, pattern upload. | Stepper interno REDIGI/FINE, percentuale workflow, azioni fisse, upload legato allo step attivo. | Componente azioni sottofase, componente upload documento, eventuale adattatore legacy workflow. | Da trasformare in card "Azioni sottofase" o congelare come legacy fino alla migrazione. |
| `frontend/src/components/procedimenti/SottofaseDocumentaleCard.vue` | Mostra stato documentale, documento corrente, storico, step operativi, apertura/scarico/Word. | Quasi tutto il pannello documentale, normalizzatori dati, apertura/scarico, helper Word, storico versioni. | Visualizzazione `StepCorrente` e sezione "step operativi documentali". | Sezione documento principale, storico versioni, azioni documento, storico azioni legacy. | Diventa card centrale della sottofase; in futuro dovra aggiungere allegati e partecipanti o integrarsi con card dedicate. |
| `frontend/src/services/procedimentoApi.js` | Client API per procedimenti, fasi, sottofasi, documentale, workflow, upload e helper Word. | Funzioni documentali, apertura/scarico, upload, fasi/sottofasi. | Nomi `getWorkflowSottofase`, `eseguiAzioneWorkflowSottofase`, `listStepOperativiSottofase`. | API documenti, API azioni sottofase, API partecipanti. | I metodi workflow restano compatibilita; i nuovi metodi dovrebbero parlare di sottofase, azioni, partecipanti e allegati. |

### Database Access

| Tabella | Uso attuale | Uso futuro possibile | Campi da conservare | Campi da rivalutare | Compatibilita nuovo modello |
| --- | --- | --- | --- | --- | --- |
| `T_Procedimenti` | Contenitore del procedimento. | Resta radice del modello. | Identificativi, codice, titolo, stato, date, priorita, campi organizzativi. | Nessuno emerso in questo step. | Alta. |
| `T_ProcedimentoFasi` | Contiene fasi del procedimento. | Resta livello padre della sequenza di sottofasi. | `IDFase`, `IDProcedimento`, `CodiceFase`, `Titolo`, `Ordine`, `StatoFase`, date, obbligatorieta/blocco. | Eventuali regole di completamento fase. | Alta. |
| `T_ProcedimentoSottofasi` | Contiene sottofasi e oggi anche campi documentali e `StepCorrente`. | Diventa fulcro del nuovo modello: stato, nota, documento principale, tipo sottofase, ordine nella fase. | `IDSottofase`, `IDFase`, `IDCatalogoSottofase`, `CodiceSottofase`, `Titolo`, `Ordine`, `StatoSottofase`, `NoteInterne`, `IDDocumentoCorrente`, `VersioneDocumento`, `DataUltimaAzione`, `UtenteUltimaAzione`, date. | `StepCorrente`, `TestoOperatore`, `HaDocumentoCollegato` come cache, significato di responsabile. | Alta se `StepCorrente` viene trattato come legacy/compatibilita e non come verita concettuale. |
| `L_CatalogoSottofasi` | Catalogo per creare/mostrare sottofasi. | Puo diventare catalogo dei tipi sottofase: REDIGI, REVISIONA, FIRMA, PROTOCOLLA, FINE, APPROVAZIONE. | Codice, titolo, descrizione, icona, colore, categoria, ordine. | Necessita futura di capability/configurazioni per tipo sottofase. | Alta. |
| `T_SottofaseDocumenti` | Storico versionato dei documenti collegati alla sottofase. | Resta base per documento principale e versioni; potra essere estesa/affiancata per allegati. | ID, `IDSottofase`, tipo, nome, estensione, path, mime, dimensione, hash, versione, data/utente, attivo. | Distinzione documento principale/allegato; relazione a documento padre se introdotta. | Alta. |
| `T_SottofaseStepOperativi` | Storico degli step interni REDIGI/FIRMA/etc. | Storico azioni legacy o sorgente per migrazione verso eventi sottofase. | ID, `IDSottofase`, codice, ordine, stato, date, note, utenti, documento/versione collegati. | Nome e significato della tabella; non deve piu guidare il modello concettuale. | Media: compatibile come storico, non come motore primario. |

### Endpoint

| Endpoint | Valutazione | Nuovo nome consigliato | Note |
| --- | --- | --- | --- |
| `GET /protocollo-monitor/sottofasi/{id_sottofase}/documentale` | Conservare e reinterpretare. | `/protocollo-monitor/sottofasi/{id_sottofase}/quadro` oppure `/documentale` resta valido. | E il piu coerente col nuovo modello: puo diventare quadro completo sottofase. |
| `GET /protocollo-monitor/sottofasi/{id_sottofase}/documenti` | Conservare. | Eventuale `/documento-principale/versioni`. | Oggi lista documenti versionati; in futuro distinguere versioni e allegati. |
| `GET /protocollo-monitor/sottofasi/{id_sottofase}/step-operativi` | Congelare/reinterpretare. | `/sottofasi/{id}/azioni-storiche` oppure `/eventi`. | Non deve piu rappresentare il workflow corrente; utile come storico legacy. |
| `GET /protocollo-monitor/sottofasi/{id_sottofase}/workflow` | Reinterpretare e poi dismettere o affiancare. | `/sottofasi/{id}/stato-operativo` oppure `/sottofasi/{id}/azioni-disponibili`. | Oggi genera step interni fissi; domani dovrebbe esporre stato/azioni della sottofase. |
| `POST /protocollo-monitor/sottofasi/{id_sottofase}/workflow/azioni` | Reinterpretare. | `/sottofasi/{id}/azioni` | Le azioni devono dipendere da tipo sottofase, partecipanti e permessi. |
| `POST /protocollo-monitor/sottofasi/{id_sottofase}/documenti` | Conservare. | Eventuale `/documento-principale/versioni`. | Upload Word versionato resta valido; cambia la regola di abilitazione. |
| `GET /protocollo-monitor/sottofase-documenti/{id_documento}/apri` | Conservare. | Nessun cambio urgente. | Endpoint documentale puro, compatibile. |
| `GET /protocollo-monitor/sottofase-documenti/{id_documento}/scarica` | Conservare. | Nessun cambio urgente. | Endpoint documentale puro, compatibile. |

### Concetto di workflow

| Tema | Valutazione |
| --- | --- |
| Cosa resta utile | Sequenza ordinata, validazione transizioni, storico azioni, backup prima delle scritture, rollback transazionale, feedback UI. |
| Cosa diventa storico azioni | `T_SottofaseStepOperativi`, record REDIGI/FIRMA/etc. gia scritti, timestamp, utente, note e documento/versione collegata. |
| Cosa va trasformato | Le azioni `AVVIA_REDAZIONE`, `INVIA_REVISIONE`, `SEGNA_FIRMATO`, `SEGNA_PROTOCOLLATO`, `CHIUDI_SOTTOFASE` diventano azioni specifiche di sottofase o transizioni tra sottofasi. |
| Reinterpretazione di `T_SottofaseStepOperativi` | Da motore del workflow interno a log legacy/eventi operativi usabile per audit e migrazione. |

### Concetto di documento

| Tema | Valutazione |
| --- | --- |
| Documento principale | Gia rappresentato da `IDDocumentoCorrente` e dal documento corrente esposto dal service documentale. |
| Versioni | Gia robuste tramite `T_SottofaseDocumenti.VersioneDocumento`, path versionato, hash e storico. |
| Documento corrente | Da conservare come puntatore alla versione attiva del documento principale. |
| Allegati futuri | Da introdurre distinguendoli dalle versioni del documento principale; possibile estensione di `T_SottofaseDocumenti` o tabella dedicata futura. |
| Apertura/scarico/helper Word | Da conservare: sono funzionalita documentali pure, poco dipendenti dal workflow. |

### Concetto di partecipanti

| Tema | Impatto futuro |
| --- | --- |
| Revisori | Associati a sottofasi di tipo `REVISIONA`; il loro stato puo determinare esito revisione e completamento. |
| Firmatari | Associati a sottofasi di tipo `FIRMA`; data/stato firma diventano attributi specifici o eventi. |
| Approvatori | Associati a sottofasi di tipo `APPROVAZIONE`; possono introdurre esiti approvato/respinto/integrazione. |
| Avatar a ventaglio | Visualizzazione sintetica dei partecipanti della sottofase, non dei soli responsabili. |
| Stato partecipante | Puo guidare colore avatar: non eseguito, completato, respinto, richiesta integrazione. |
| Completamento automatico | Una sottofase puo completarsi quando tutti i partecipanti obbligatori hanno completato l'azione richiesta, secondo regole del tipo sottofase. |

### Cosa si conserva

| Area | Elementi da conservare | Motivazione |
| --- | --- | --- |
| Documenti | Upload Word, documento corrente, storico versioni, hash, dimensione, path versionato. | Sono coerenti col documento protagonista. |
| Access safety | Backup obbligatorio, rollback DB, rollback file su errore. | Restano regole fondamentali per ogni scrittura. |
| Apertura file | Apri, scarica, helper Word locale. | Sono funzioni documentali indipendenti dal workflow interno. |
| Architettura | Router sottile, service layer, repository, dependency container. | La separazione gia introdotta facilita il refactoring. |
| UI | Pannello documentale, selezione fase/sottofase, refresh dopo azione. | Sono compatibili col modello sottofase come unita operativa. |

### Cosa si reinterpreta

| Elemento | Reinterpretazione proposta |
| --- | --- |
| `StepCorrente` | Campo legacy/compatibilita o indicatore temporaneo durante migrazione, non verita concettuale. |
| `T_SottofaseStepOperativi` | Storico azioni/eventi legacy, non workflow interno obbligatorio. |
| `WorkflowSottofaseCard.vue` | Da card workflow interno a card azioni sottofase o componente legacy congelato. |
| Endpoint `/workflow` | Da stato di step interni a stato operativo/azioni disponibili della sottofase. |
| Endpoint `/workflow/azioni` | Da avanzamento sequenza fissa a esecuzione azioni specifiche della sottofase. |
| Upload consentito in REDIGI/REVISIONA | Da controllo su step attivo a controllo su tipo/stato sottofase e permessi/partecipanti. |

### Cosa si dismette o si congela

| Elemento | Decisione prudenziale |
| --- | --- |
| Sequenza interna obbligatoria REDIGI -> REVISIONA -> FIRMA -> PROTOCOLLA -> FINE | Congelare come compatibilita, poi dismettere come modello primario. |
| Enum azioni workflow fisse | Congelare finche esistono dati/endpoint legacy; sostituire con azioni per tipo sottofase. |
| Progress bar percentuale workflow interno | Dismettere nella UI futura o limitarla a vista legacy. |
| Logica di completamento basata su `StepCorrente=FINE` | Reinterpretare con stato sottofase e regole partecipanti/documento. |
| Sezione "step operativi documentali" nel pannello principale | Spostare in storico azioni/audit, non nel cuore della UI sottofase. |

### Nuovi concetti da introdurre

| Concetto | Scopo |
| --- | --- |
| Tipo sottofase | Stabilire capacita, azioni, partecipanti e UI specifica di REDIGI/REVISIONA/FIRMA/PROTOCOLLA/FINE. |
| PartecipanteSottofase | Modellare utente, ruolo, stato, data azione e note. |
| AzioneSottofase | Sostituire l'azione workflow fissa con azioni specifiche e validabili per tipo sottofase. |
| Stato partecipante | Guidare avatar, completamento e blocchi operativi. |
| Allegato documento principale | Distinguere versioni del documento principale da file accessori. |
| Storico azioni sottofase | Evoluzione concettuale di `T_SottofaseStepOperativi` verso audit/eventi. |

### Proposta di percorso graduale di refactoring

1. Step 30L-21C: produrre mappatura esplicita tra workflow attuale e nuovo modello, senza scritture.
2. Separare nel frontend il pannello documentale dalle azioni operative.
3. Introdurre un adattatore backend che esponga lo stato legacy come storico, non come workflow primario.
4. Definire contratti per `PartecipanteSottofase` e azioni specifiche di sottofase.
5. Agganciare avatar/stati partecipante in sola lettura o mock controllato.
6. Cambiare la regola upload Word da step attivo a tipo/stato sottofase.
7. Mantenere endpoint legacy durante la transizione, aggiungendo nuovi endpoint solo in step dedicati.
8. Migrare la UI da `WorkflowSottofaseCard.vue` a una card sottofase semplificata con documento, partecipanti e azioni.
9. Congelare `T_SottofaseStepOperativi` come storico legacy prima di eventuali tabelle/eventi futuri.

### Valutazione percentuale

| Categoria | Stima | Motivazione |
| --- | --- | --- |
| Codice da conservare | 55% | Documentale, apertura/scarico, helper Word, repository documenti, router sottile, container e vista fase/sottofase restano in gran parte validi. |
| Codice da reinterpretare | 30% | Service workflow, endpoint workflow, card workflow e step operativi vanno riletti come compatibilita/storico o azioni sottofase. |
| Codice da riscrivere | 10% | Serviranno nuovi contratti per partecipanti, azioni specifiche e UI semplificata. |
| Codice da eliminare | 5% | Probabile rimozione futura di progress workflow interno, enum azioni fisse e sezioni UI legacy dopo migrazione. |

### Prossimi step consigliati

| Step | Obiettivo |
| --- | --- |
| Step 30L-21C | Mappatura workflow attuale / nuovo modello. |
| Step 30L-22 | Partecipanti sottofase. |
| Step 30L-23 | Avatar a ventaglio. |
| Step 30L-24 | Allegati documento principale. |
| Step 30L-25 | Refactoring UI sottofase semplificata. |

## Step 30L-21C – Mappatura workflow attuale / nuovo modello

Questo step e esclusivamente di analisi e progettazione. Non introduce
modifiche a codice, database, schema Access, endpoint o frontend.

### Obiettivo della mappatura

Lo scopo e capire come riutilizzare il lavoro gia fatto senza perdere dati,
funzionalita e investimenti. Il modello attuale vede `REDIGI`, `REVISIONA`,
`FIRMA`, `PROTOCOLLA` e `FINE` come step interni del workflow di una sottofase.
Il nuovo modello li reinterpreta come sottofasi vere e proprie, o come tipi di
sottofase, attraversate dal documento principale.

### Mappatura concettuale

| Modello attuale | Nuovo modello | Esito | Note |
| --- | --- | --- | --- |
| `FASE` | `FASE` | Conservare | La fase resta il contenitore ordinato delle sottofasi. |
| `SOTTOFASE` come contenitore del workflow | `SOTTOFASE` come unita operativa reale | Reinterpretare | La sottofase non e piu solo il contenitore di REDIGI/FIRMA/etc.; puo essere REDIGI, REVISIONA, FIRMA, PROTOCOLLA, FINE o altra sottofase. |
| Workflow `REDIGI` | Sottofase o tipo sottofase `REDIGI` | Trasformare | Redazione come sottofase con stato, nota, documento principale, partecipanti/operatori e azioni proprie. |
| Workflow `REVISIONA` | Sottofase o tipo sottofase `REVISIONA` | Trasformare | Revisione come sottofase con revisori, commenti, esito e versioni documento. |
| Workflow `FIRMA` | Sottofase o tipo sottofase `FIRMA` | Trasformare | Firma come sottofase con firmatari, stato firma e data firma. |
| Workflow `PROTOCOLLA` | Sottofase o tipo sottofase `PROTOCOLLA` | Trasformare | Protocollazione come sottofase con numero protocollo, data protocollo e operatori. |
| Workflow `FINE` | Sottofase o stato conclusivo `FINE` | Reinterpretare | Puo restare una sottofase di chiusura oppure diventare stato finale della sequenza, da decidere nel refactoring. |
| `StepCorrente` | Stato/posizione legacy nella migrazione | Congelare | Utile per leggere lo stato dei dati gia scritti, non per guidare il nuovo modello. |
| `T_SottofaseStepOperativi` | Storico azioni/eventi legacy | Reinterpretare | Non e piu la fonte primaria del modello, ma conserva memoria operativa. |

### Mappatura database

| Tabella | Significato attuale | Significato futuro | Compatibilita | Necessita di migrazione | Riutilizzo stimato |
| --- | --- | --- | --- | --- | --- |
| `T_ProcedimentoSottofasi` | Record della sottofase, stato, ordine, campi documentali e `StepCorrente`. | Record della sottofase reale o del tipo sottofase attraversato dal documento. | Alta. | Migrazione logica: interpretare `CodiceSottofase`/catalogo come tipo sottofase e congelare `StepCorrente` come legacy. | 80% |
| `T_SottofaseDocumenti` | Storico versionato dei documenti collegati a una sottofase. | Storico versioni del documento principale; base futura per distinguere versioni e allegati. | Molto alta. | Nessuna migrazione distruttiva; eventuale estensione futura per allegati. | 90% |
| `T_SottofaseStepOperativi` | Storico degli step interni completati nel workflow della sottofase. | Storico azioni/eventi legacy utile per audit, mapping e continuita. | Media. | Richiede reinterpretazione: da motore workflow a log storico. | 60% |

### Mappatura endpoint

| Endpoint attuale | Decisione | Nuovo ruolo consigliato | Note |
| --- | --- | --- | --- |
| `GET /protocollo-monitor/sottofasi/{id_sottofase}/workflow` | Congelare e reinterpretare | Lettura stato legacy o azioni disponibili durante la transizione. | Da non eliminare finche la UI usa `WorkflowSottofaseCard.vue`. |
| `POST /protocollo-monitor/sottofasi/{id_sottofase}/workflow/azioni` | Reinterpretare, poi sostituire | Futuro `POST /sottofasi/{id}/azioni`. | Le azioni devono dipendere dal tipo sottofase e dai partecipanti. |
| `GET /protocollo-monitor/sottofasi/{id_sottofase}/documentale` | Conservare | Quadro documentale/sottofase. | Puo diventare il centro del nuovo pannello sottofase. |
| `GET /protocollo-monitor/sottofasi/{id_sottofase}/documenti` | Conservare | Versioni documento principale. | In futuro distinguere da allegati. |
| `POST /protocollo-monitor/sottofasi/{id_sottofase}/documenti` | Conservare e reinterpretare | Upload nuova versione documento principale. | La regola di abilitazione passera da step REDIGI/REVISIONA a tipo/stato sottofase. |
| `GET /protocollo-monitor/sottofase-documenti/{id_documento}/apri` | Conservare | Apertura documento/versione. | Compatibile con nuovo modello. |
| `GET /protocollo-monitor/sottofase-documenti/{id_documento}/scarica` | Conservare | Scarico documento/versione. | Compatibile con nuovo modello. |

### Mappatura frontend

| Componente | Cosa resta | Cosa cambia nome | Cosa cambia funzione | Cosa viene separato |
| --- | --- | --- | --- | --- |
| `WorkflowSottofaseCard.vue` | Dialog azione, gestione loading/errori, emit refresh, pattern upload. | Probabile rinomina in card azioni sottofase o congelamento come legacy. | Da stepper workflow interno a pannello azioni specifiche della sottofase. | Upload documento, lista azioni, storico legacy. |
| `SottofaseDocumentaleCard.vue` | Documento corrente, storico versioni, apri/scarica, helper Word, normalizzazione dati. | Puo diventare `SottofaseDocumentoCard` o restare documentale. | Da pannello documentale piu step operativi a pannello documento principale/versioni/allegati. | Storico step operativi va spostato in storico azioni/audit. |
| `ProcedimentoDettaglioView.vue` | Layout fase/sottofase, selezione sottofase, avatar, reload dopo aggiornamento. | Il linguaggio "workflow" va ridotto o sostituito con "fasi/sottofasi". | La sequenza REDIGI/FIRMA/etc. viene mostrata come sottofasi della fase, non come step dentro una card. | Timeline sottofasi, pannello documentale, partecipanti, azioni. |

### Mappatura dati gia scritti

| Categoria | Reinterpretazione senza perdita? | Motivazione |
| --- | --- | --- |
| `StepCorrente` | PARZIALMENTE | Indica dove si trovava il workflow interno; puo mappare la sottofase/tipo futuro, ma non contiene da solo partecipanti o funzionalita specifiche. |
| Storico workflow | SI | I record in `T_SottofaseStepOperativi` conservano codice step, stato, date, note e utenti; possono diventare storico azioni legacy. |
| Azioni eseguite | PARZIALMENTE | Sono ricostruibili dagli step completati e dalle note, ma il significato va tradotto in azioni sottofase o transizioni. |
| Documenti caricati | SI | Path, hash, dimensione, tipo, utente e data restano validi. |
| Versioni esistenti | SI | La numerazione versionata e coerente con il nuovo documento principale. |

Conclusione sui dati: i dati gia presenti possono essere reinterpretati senza
perdita sostanziale del contenuto documentale. La perdita potenziale riguarda
solo il significato operativo fine delle azioni, perche oggi e codificato come
avanzamento lineare e non come azione specifica di una sottofase reale.

### Mappatura delle azioni

| Azione attuale | Decisione | Nuova interpretazione possibile |
| --- | --- | --- |
| `AVVIA_REDAZIONE` | Trasformare | `COMPLETA_REDAZIONE`, `SALVA_BOZZA` o transizione da sottofase REDIGI a REVISIONA. |
| `INVIA_REVISIONE` | Trasformare | `INVIA_A_REVISIONE`, `ESITO_REVISIONE_POSITIVO` o transizione da REVISIONA a FIRMA. |
| `SEGNA_FIRMATO` | Trasformare | `REGISTRA_FIRMA` o completamento partecipante con ruolo `FIRMATARIO`. |
| `SEGNA_PROTOCOLLATO` | Trasformare | `REGISTRA_PROTOCOLLO` con numero/data protocollo quando disponibili. |
| `CHIUDI_SOTTOFASE` | Mantenere come concetto, trasformare come implementazione | Diventa `COMPLETA_SOTTOFASE` o completamento automatico quando regole documento/partecipanti sono soddisfatte. |

### Compatibilita documentale

| Elemento | Riutilizzo | Eventuali modifiche |
| --- | --- | --- |
| Documento principale | Alto | Mantenere `IDDocumentoCorrente` come puntatore alla versione corrente. |
| Versioni | Molto alto | Conservare `T_SottofaseDocumenti.VersioneDocumento`; distinguere in futuro versioni da allegati. |
| Documento corrente | Alto | Resta la versione attiva del documento principale della sottofase. |
| Helper Word | Alto | Nessuna modifica concettuale; resta servizio locale di apertura Word. |
| Apri | Alto | Endpoint e UI restano compatibili. |
| Scarica | Alto | Endpoint e UI restano compatibili. |

### Partecipanti: preparazione Step 30L-22

| Ruolo | Dove si collega | Impatto sulla sottofase | Completamento automatico possibile |
| --- | --- | --- | --- |
| `REVISORE` | Sottofase `REVISIONA` o tipo revisione. | Determina esito revisione, note e richieste integrazione. | Si, quando tutti i revisori obbligatori hanno esito positivo; no se uno respinge o chiede integrazione. |
| `FIRMATARIO` | Sottofase `FIRMA`. | Determina stato firma e data firma. | Si, quando tutti i firmatari obbligatori hanno firmato. |
| `APPROVATORE` | Sottofase `APPROVAZIONE` o sottofase personalizzata. | Determina approvazione, rigetto o richiesta integrazione. | Si, secondo quorum o unanimita decisa dal tipo sottofase. |
| `OPERATORE` | Qualsiasi sottofase operativa, in particolare REDIGI/PROTOCOLLA. | Esegue azioni pratiche e aggiorna stato/documento. | Si, se l'azione operatore richiesta e completata. |
| `OSSERVATORE` | Qualsiasi sottofase. | Visibilita e tracciamento senza potere bloccante. | Di norma no, salvo regole future. |

### Strategia di migrazione

| Fase | Nome | Strategia | Obiettivo |
| --- | --- | --- | --- |
| Fase 1 | Convivenza | Mantenere workflow legacy e nuovo modello concettuale documentato. | Evitare rotture e preservare operativita esistente. |
| Fase 2 | Reinterpretazione | Leggere `StepCorrente` e `T_SottofaseStepOperativi` come stato/storico legacy. | Rendere esplicito il mapping senza migrare fisicamente i dati. |
| Fase 3 | Semplificazione | Separare UI documentale, azioni sottofase, partecipanti e storico. | Ridurre dipendenza da `WorkflowSottofaseCard.vue` e dalla sequenza interna. |
| Fase 4 | Nuovo modello | Introdurre sottofasi/tipi sottofase, partecipanti, allegati e azioni specifiche. | Il documento attraversa sottofasi reali; il workflow interno non e piu il modello primario. |

### Quanto lavoro si conserva

Stima motivata: circa 70% del lavoro svolto puo essere conservato.

| Area | Conservazione stimata | Motivo |
| --- | --- | --- |
| Documentale | 85-90% | Upload, versionamento, documento corrente, storico, apertura/scarico e helper Word restano centrali. |
| Backend architetturale | 60-70% | Router, service, repository, backup e rollback restano validi; cambia il dominio workflow. |
| Frontend | 50-60% | Layout fase/sottofase e card documentale restano; card workflow va trasformata. |
| Database Access | 70-80% | Tabelle principali restano compatibili; `T_SottofaseStepOperativi` diventa storico legacy. |
| Azioni workflow | 35-45% | Le azioni sono utili come intenzioni operative, ma vanno rinominate e spostate nel modello azioni sottofase. |

### Rischi principali

- Confondere la sottofase reale con lo step legacy durante la convivenza.
- Usare `StepCorrente` come fonte primaria anche dopo l'introduzione dei tipi sottofase.
- Mescolare versioni del documento principale e allegati futuri.
- Perdere il significato operativo delle azioni gia eseguite se non vengono mappate prima del refactoring.
- Introdurre partecipanti senza regole chiare di completamento.

## Step 30L-22 – Partecipanti sottofase

Questo step introduce la prima base dati e backend per il concetto di
`PartecipanteSottofase`, senza costruire ancora avatar a ventaglio e senza
modificare il frontend.

### Obiettivo

Collegare alla sottofase partecipanti con ruolo, stato, dati visuali minimi,
note e date operative, mantenendo compatibilita con Access oggi e con una
futura migrazione PostgreSQL.

### Ruoli e stati iniziali

| Tipo | Valori |
| --- | --- |
| Ruoli | `OPERATORE`, `REVISORE`, `FIRMATARIO`, `PROTOCOLLATORE`, `APPROVATORE`, `OSSERVATORE` |
| Stati | `ASSEGNATO`, `IN_ATTESA`, `IN_CORSO`, `COMPLETATO`, `RESPINTO`, `ANNULLATO` |

### Database Access

Tabella creata: `T_SottofasePartecipanti`.

Campi:

- `IDPartecipante` autoincrement primary key;
- `IDSottofase`;
- `IDUtente`;
- `NomeVisualizzato`;
- `Email`;
- `Ruolo`;
- `StatoPartecipante`;
- `Ordine`;
- `ColoreAvatar`;
- `Iniziali`;
- `DataAssegnazione`;
- `DataAzione`;
- `NotePartecipante`;
- `Attivo`;
- `DataCreazione`;
- `DataModifica`.

Indici creati:

- `IX_T_SottofasePartecipanti_IDSottofase`;
- `IX_T_SottofasePartecipanti_Ruolo`;
- `IX_T_SottofasePartecipanti_Stato`;
- `IX_T_SottofasePartecipanti_Attivo`.

Backup Access creato prima della modifica schema:

```text
C:\Users\fintu\CloudVVF\Documents\Sviluppo\Grisu\Backup\ProtocolloMonitor_BACKUP_20260601_112002.accdb
```

La creazione schema e idempotente: tabella e indici vengono creati solo se non
esistono.

### Backend

File creati:

- `backend/schemas/sottofase_partecipanti.py`;
- `backend/repositories/sottofase_partecipanti_repository.py`;
- `backend/services/sottofase_partecipanti_service.py`;
- `tests/test_sottofase_partecipanti_repository.py`;
- `tests/test_sottofase_partecipanti_service.py`;
- `tests/test_sottofase_partecipanti_endpoint.py`.

File modificati:

- `backend/api/routes/protocollo_monitor.py`;
- `backend/core/dependency_container.py`;
- `ROADMAP_PROTOCOLLOMONITOR.md`.

Endpoint aggiunti:

| Metodo | Endpoint | Scopo |
| --- | --- | --- |
| `GET` | `/protocollo-monitor/sottofasi/{id_sottofase}/partecipanti` | Restituisce i partecipanti attivi della sottofase. |
| `POST` | `/protocollo-monitor/sottofasi/{id_sottofase}/partecipanti` | Inserisce un partecipante con backup Access e scrittura controllata. |

Endpoint rimandato:

- `PATCH /protocollo-monitor/sottofasi/{id_sottofase}/partecipanti/{id_partecipante}/stato`, da valutare in step successivo per non allargare troppo il perimetro.

### Validazioni implementate

- `nomeVisualizzato` obbligatorio e non vuoto;
- `ruolo` obbligatorio e ammesso;
- `statoPartecipante` obbligatorio e ammesso;
- email opzionale con validazione semplice;
- iniziali normalizzate se presenti;
- iniziali calcolate se mancanti;
- verifica esistenza `IDSottofase`;
- controllo duplicato evidente su stessa sottofase, email e ruolo;
- backup Access prima dell'insert;
- insert transazionale con commit/rollback.

### Test

Test mirati aggiunti:

- creazione tabella se assente;
- non ricreazione tabella/indici se esistenti;
- GET partecipanti vuoto;
- POST partecipante valido;
- ruolo non ammesso;
- stato non ammesso;
- nome mancante;
- duplicato;
- rollback su errore insert;
- calcolo iniziali se mancanti;
- backup prima della scrittura.

Risultato test mirati:

```text
21 passed
```

### Vincoli rispettati

- `Python/server_protocollo.py` non modificato.
- Frontend non modificato.
- Workflow legacy non modificato.
- Nessun dato reale popolato automaticamente.
- Nessun commit eseguito.

## Step 30L-23 – Timeline operativa sottofase

Questo step e esclusivamente architetturale e documentale. Non introduce
modifiche a codice, database, schema Access, endpoint o frontend.

### Nuova decisione architetturale

Ogni sottofase contiene una timeline operativa composta da step ordinati
cronologicamente. Gli step precaricati tipici possono essere:

- `REDIGI`;
- `REVISIONA`;
- `FIRMA`;
- `PROTOCOLLA`.

Questi step compaiono inizialmente grigi e si colorano progressivamente quando
vengono completati. La timeline non deve essere rigida: gli step possono essere
eliminati se non servono, aggiunti, riordinati o sostituiti con step intermedi.

Esempi di step/eventi operativi:

- `CHIAMATA`;
- `EMAIL`;
- `APPUNTAMENTO`;
- `PARERE`;
- `SOPRALLUOGO`;
- `ALTRO`.

### Modello concettuale dello step timeline

Ogni step della timeline puo avere:

- codice step;
- titolo;
- tipo step;
- ordine;
- stato;
- data prevista;
- data completamento;
- nota;
- documento collegato opzionale;
- partecipanti assegnati.

La sottofase mantiene quindi il proprio stato complessivo, ma la timeline
descrive il percorso operativo interno, flessibile e adattabile al caso reale.

### Reinterpretazione di `T_SottofaseStepOperativi`

`T_SottofaseStepOperativi` puo essere reinterpretata come tabella della timeline
operativa della sottofase.

Nel modello precedente conteneva gli step del workflow interno rigido
`REDIGI -> REVISIONA -> FIRMA -> PROTOCOLLA -> FINE`. Nel modello aggiornato
puo diventare la base per memorizzare step operativi ordinati, anche non
standard, mantenendo compatibilita con i dati gia scritti.

Mappatura concettuale:

| Campo/concetto attuale | Nuovo significato possibile |
| --- | --- |
| `CodiceStep` | Codice dello step timeline, standard o personalizzato. |
| `Ordine` | Posizione cronologica/visuale nella timeline. |
| `StatoStep` | Stato dello step: non avviato, in corso, completato, respinto, annullato o equivalenti futuri. |
| `DataAvvio` | Data di avvio o presa in carico dello step. |
| `DataCompletamento` | Data di completamento dello step. |
| `NoteStep` | Nota operativa dello step. |
| `UtenteAssegnato` / `UtenteCompletamento` | Campi legacy utili, ma da superare con partecipanti assegnati allo step. |
| `IDDocumentoSottofase` | Documento/versione collegata opzionalmente allo step. |
| `VersioneDocumento` | Versione documento collegata allo step. |

### Partecipanti collegati alla sottofase o allo step

I partecipanti possono essere collegati:

- alla sottofase in generale;
- a uno specifico step della timeline.

Esempi:

- `REVISIONA`: revisori assegnati;
- `FIRMA`: firmatari assegnati;
- `PROTOCOLLA`: protocollatori assegnati;
- `APPUNTAMENTO`: partecipanti all'appuntamento;
- `EMAIL`: destinatari o referenti.

`T_SottofasePartecipanti` oggi collega il partecipante alla sottofase tramite
`IDSottofase`. In una fase futura potrebbe dover collegare il partecipante anche
a uno step specifico tramite un futuro `IDStepSottofase`, senza perdere la
possibilita di partecipanti generali della sottofase.

### UI desiderata

La UI futura dovra rappresentare la timeline in modo orizzontale:

- step grigi se non completati;
- step colorati se completati;
- step attivo evidenziato;
- avatar a ventaglio sopra lo step quando ci sono partecipanti assegnati;
- possibilita futura di aggiungere uno step tra due step esistenti.

La timeline orizzontale sostituisce gradualmente la lettura rigida del workflow
interno, ma conserva l'idea gia realizzata di avanzamento visuale.

### Cosa si conserva

| Elemento | Decisione |
| --- | --- |
| `T_SottofaseStepOperativi` | Conservare e reinterpretare come timeline operativa. |
| Partecipanti | Conservare `T_SottofasePartecipanti` come base per partecipanti di sottofase. |
| Documento principale | Conservare il modello documentale corrente. |
| Versionamento | Conservare storico versioni e documento corrente. |
| Backup/rollback | Conservare come regola obbligatoria per ogni futura scrittura o modifica schema. |

### Cosa va evoluto

| Area | Evoluzione richiesta |
| --- | --- |
| Collegamento partecipanti-step | Valutare un futuro `IDStepSottofase` su partecipanti o una tabella ponte dedicata. |
| UI timeline orizzontale | Progettare una visualizzazione compatta, leggibile e coerente con stati e partecipanti. |
| Aggiunta/eliminazione step | Definire regole per inserire, eliminare e riordinare step senza perdere storico. |
| Avatar a ventaglio | Collegare avatar allo step quando i partecipanti sono specifici della timeline. |
| Tipi step | Distinguere step standard da eventi operativi personalizzati. |

### Rischi architetturali

- Confondere sottofase e step timeline: la sottofase resta il contenitore
  operativo, la timeline ne descrive il percorso interno.
- Sovraccaricare `T_SottofaseStepOperativi` senza chiarire quali campi sono
  legacy e quali sono canonici.
- Collegare partecipanti solo alla sottofase quando invece alcuni ruoli sono
  specifici dello step.
- Rendere la timeline troppo rigida, riproducendo il problema del workflow
  precedente.
- Introdurre riordino/eliminazione step senza una strategia di storico e audit.

## Step 30L-23C – Timeline sequenziale dinamica con blocco di avanzamento

Questo step e esclusivamente architetturale. Non introduce modifiche a codice,
database, schema Access, endpoint o frontend.

### Decisione definitiva

La timeline operativa della sottofase non e libera. La timeline e:

- sequenziale;
- ordinata;
- bloccante.

Gli step possono essere aggiunti, eliminati e riordinati, ma l'esecuzione resta
vincolata all'ordine della timeline.

Regola fondamentale:

```text
Uno step puo essere eseguito soltanto se tutti gli step precedenti risultano completati.
```

Esempio standard:

```text
REDIGI -> REVISIONA -> FIRMA -> PROTOCOLLA
```

Se `REDIGI` non e completata, `REVISIONA`, `FIRMA` e `PROTOCOLLA` restano
bloccate.

Esempio con step aggiuntivi:

```text
REDIGI -> CHIAMATA -> EMAIL -> REVISIONA -> APPUNTAMENTO -> FIRMA -> PROTOCOLLA
```

Finche `CHIAMATA` non e completata, `EMAIL`, `REVISIONA`, `APPUNTAMENTO`,
`FIRMA` e `PROTOCOLLA` restano bloccate.

### Stati concettuali dello step

| Stato | Significato | Visualizzazione desiderata |
| --- | --- | --- |
| `LOCKED` | Step bloccato perche uno o piu step precedenti non sono completati. | Grigio. |
| `ACTIVE` | Primo step non completato, attualmente eseguibile. | Giallo o evidenziato. |
| `COMPLETED` | Step completato. | Colore del tipo step. |
| `REJECTED` | Step respinto o con esito negativo. | Rosso. |
| `CANCELLED` | Step annullato e non piu operativo. | Grigio scuro. |

### Regola di calcolo dello step attivo

Lo step attivo e:

```text
il primo step non completato della timeline
```

Conseguenza architetturale:

- `StepCorrente` non deve piu essere il concetto principale;
- `StepCorrente` puo diventare dato derivato;
- `StepCorrente` puo restare cache o ottimizzazione temporanea;
- `StepCorrente` puo essere eliminato in futuro se la timeline diventa la fonte autorevole.

La fonte concettuale primaria diventa l'elenco ordinato degli step con il loro
stato.

### Impatto su `T_SottofaseStepOperativi`

`T_SottofaseStepOperativi` viene reinterpretata come timeline operativa della
sottofase. Ogni record rappresenta uno step della timeline.

Campi concettuali associati:

- tipo step;
- ordine;
- stato;
- data prevista;
- data completamento;
- note;
- documento collegato;
- partecipanti.

Mappatura prudenziale:

| Concetto timeline | Campo attuale o futuro |
| --- | --- |
| Tipo step | Oggi `CodiceStep`; in futuro possibile distinzione `TipoStep`/`CodiceStep`. |
| Ordine | `Ordine`. |
| Stato | `StatoStep`, da normalizzare verso stati concettuali `LOCKED`, `ACTIVE`, `COMPLETED`, `REJECTED`, `CANCELLED` o mapping equivalente. |
| Data prevista | Campo futuro da valutare. |
| Data completamento | `DataCompletamento`. |
| Note | `NoteStep`. |
| Documento collegato | `IDDocumentoSottofase` e `VersioneDocumento`. |
| Partecipanti | Collegamento futuro con partecipanti generali o specifici dello step. |

### Impatto sui partecipanti

Un partecipante puo essere:

- generale della sottofase;
- collegato a uno specifico step della timeline.

Esempi:

- `REVISIONA`: revisori assegnati;
- `FIRMA`: firmatari assegnati;
- `PROTOCOLLA`: protocollatori assegnati.

Il completamento dello step puo dipendere dai partecipanti. Per esempio:

- uno step `REVISIONA` puo completarsi quando tutti i revisori richiesti hanno completato con esito positivo;
- uno step `FIRMA` puo completarsi quando tutti i firmatari richiesti hanno firmato;
- uno step `PROTOCOLLA` puo completarsi quando il protocollatore ha registrato la protocollazione.

Il completamento automatico guidato dai partecipanti va trattato come regola
dedicata futura, non come effetto implicito non documentato.

### UI target

La timeline target e orizzontale:

```text
○ REDIGI ─── ○ REVISIONA ─── ○ FIRMA ─── ○ PROTOCOLLA
```

Comportamenti UI desiderati:

- step `LOCKED` grigi e non eseguibili;
- step `ACTIVE` evidenziato;
- step `COMPLETED` colorato in base al tipo step;
- step `REJECTED` rosso;
- step `CANCELLED` grigio scuro;
- avatar a ventaglio sopra lo step quando ci sono partecipanti;
- inserimento futuro di step tra due punti;
- eliminazione step;
- riordino controllato.

### Regole documentate

| Tema | Regola |
| --- | --- |
| Avanzamento | Solo il primo step non completato e attivo. |
| Blocco | Tutti gli step successivi allo step attivo restano bloccati. |
| Completamento | Il completamento di uno step sblocca il successivo primo non completato. |
| Step aggiunti | Uno step inserito nella sequenza partecipa subito al blocco di avanzamento. |
| Step eliminati | L'eliminazione deve essere controllata e non deve perdere storico rilevante. |
| Step annullati | Uno step `CANCELLED` non dovrebbe bloccare la timeline se formalmente escluso dal percorso operativo. |
| Step respinti | Uno step `REJECTED` blocca il proseguimento finche non viene risolto o annullato secondo regole future. |

### Rischi architetturali

- Usare `StepCorrente` come fonte primaria invece della timeline ordinata.
- Introdurre stati UI senza un mapping chiaro con `StatoStep`.
- Consentire eliminazioni fisiche di step gia eseguiti, perdendo storico.
- Trattare `CANCELLED` e `REJECTED` come varianti estetiche invece che come stati con impatto sul blocco.
- Collegare partecipanti allo step senza distinguere partecipanti generali della sottofase.
- Automatizzare il completamento tramite partecipanti senza regole di quorum, obbligatorieta o esito.

## Step 30L-24 – Avatar a ventaglio su timeline

Questo step e di progettazione UI/UX. Non introduce modifiche a codice,
database, schema Access, endpoint o frontend.

### Obiettivo UX

Gli avatar a ventaglio devono permettere all'utente di capire immediatamente:

- chi deve intervenire;
- chi ha gia completato;
- chi e in ritardo o bloccato;
- chi ha respinto;
- dove si trova il blocco del procedimento.

Gli avatar rappresentano visivamente i partecipanti collegati a uno step della
timeline. I partecipanti generali della sottofase restano possibili, ma vanno
visualizzati in un'area distinta per evitare confusione.

### Layout desiderato

La timeline resta orizzontale:

```text
REDIGI --- REVISIONA --- FIRMA --- PROTOCOLLA
```

Gli avatar dello step vengono disposti sopra il punto della timeline, con
effetto a ventaglio e lieve sovrapposizione controllata.

Esempio concettuale:

```text
             [MR]
        [GB]      [LV]
REDIGI --- REVISIONA --- FIRMA --- PROTOCOLLA
```

Regole layout:

| Tema | Regola UX |
| --- | --- |
| Posizione | Avatar sopra lo step a cui sono collegati. |
| Ventaglio | Primo avatar centrato, successivi sfalsati lateralmente. |
| Sovrapposizione | Leggera sovrapposizione per ridurre ingombro, senza rendere illeggibili iniziali o bordo stato. |
| Altezza | Area avatar riservata sopra la timeline per evitare collisioni con linea e label. |
| Step attivo | Avatar dello step attivo piu evidenti rispetto agli step bloccati. |

### Numero avatar visibili

| Numero partecipanti | Visualizzazione |
| --- | --- |
| 1 | Un avatar centrato sopra lo step. |
| 2 | Due avatar affiancati con lieve sovrapposizione. |
| 3 | Ventaglio compatto: uno centrale, due laterali. |
| 4-10 | Mostrare massimo 3 o 4 avatar principali piu aggregatore `+N`. |
| Oltre 10 | Mostrare aggregatore prevalente, ad esempio `+10`, con dettaglio su click. |

L'aggregatore deve indicare quanti partecipanti non sono visibili:

- `+3`;
- `+5`;
- `+N`.

L'espansione puo avvenire tramite popover, menu o pannello laterale futuro,
mostrando l'elenco completo dei partecipanti dello step.

### Stati avatar

| Stato partecipante | Visualizzazione |
| --- | --- |
| `ASSEGNATO` | Grigio. |
| `IN_CORSO` | Giallo. |
| `COMPLETATO` | Colore personale/avatar. |
| `RESPINTO` | Rosso. |
| `ANNULLATO` | Grigio scuro. |

Se non e disponibile un'immagine profilo, l'avatar mostra le iniziali. Le
iniziali restano la fallback principale per garantire leggibilita anche senza
anagrafica utenti completa.

### Informazioni al passaggio mouse o click

Tooltip o popover devono mostrare:

- nome;
- ruolo;
- stato;
- data ultima azione;
- note sintetiche.

Su desktop il passaggio mouse puo aprire un tooltip leggero. Su tablet e mobile
il click/tap deve aprire una scheda compatta o un pannello con le stesse
informazioni.

### Ruoli e riconoscibilita

Ruoli da rappresentare:

- `OPERATORE`;
- `REVISORE`;
- `FIRMATARIO`;
- `PROTOCOLLATORE`;
- `APPROVATORE`;
- `OSSERVATORE`.

Possibili segnali visuali:

| Segnale | Uso consigliato |
| --- | --- |
| Badge ruolo | Piccolo badge o sigla sul bordo dell'avatar. |
| Icona ruolo | Utile nei dettagli/tooltip, da evitare se rende l'avatar troppo affollato. |
| Colore ruolo | Da usare con prudenza: lo stato deve restare piu importante del ruolo. |

Priorita visuale:

1. Stato del partecipante.
2. Identita del partecipante.
3. Ruolo.

### Relazione con lo step

Un avatar puo rappresentare:

- partecipante collegato allo step;
- partecipante generale della sottofase.

Regola UX:

- gli avatar sopra la timeline rappresentano partecipanti dello step;
- i partecipanti generali della sottofase vanno mostrati in una barra superiore
  o in un'area dedicata della sottofase.

Questa distinzione evita che un osservatore generale sembri responsabile di uno
step specifico.

### Partecipanti generali della sottofase

Possibili collocazioni:

| Opzione | Valutazione |
| --- | --- |
| Barra superiore della sottofase | Buona per mostrare operatori/osservatori generali sempre visibili. |
| Area dedicata nel pannello sottofase | Buona per dettaglio completo senza affollare la timeline. |
| Misto | Barra con pochi avatar principali e dettaglio espandibile. |

La scelta consigliata e mista: barra superiore sintetica e dettaglio espandibile
nel pannello sottofase.

### Completamento automatico: preparazione Step 30L-28

Gli avatar non sono solo decorazione: rappresentano stati che potranno guidare
il completamento automatico dello step.

Esempio:

```text
REVISIONA
3 revisori assegnati
tutti COMPLETATO -> step REVISIONA completato
```

Modelli possibili:

| Modello | Descrizione |
| --- | --- |
| Tutti | Lo step si completa quando tutti i partecipanti richiesti completano. |
| Maggioranza | Lo step si completa quando la maggioranza ha completato positivamente. |
| Quorum configurabile | Lo step si completa al raggiungimento di una soglia definita. |

Queste regole non vanno implementate nello step UI/UX: vanno documentate ora e
formalizzate nello Step 30L-28.

### Responsive

| Contesto | Comportamento |
| --- | --- |
| Desktop | Avatar a ventaglio completi sopra ogni step, con tooltip al passaggio mouse. |
| Tablet | Avatar piu compatti, massimo 2 o 3 visibili, aggregatore piu frequente. |
| Mobile | Avatar aggregati, dettaglio su tap; timeline eventualmente scrollabile orizzontalmente. |

La timeline deve restare leggibile anche quando molti step hanno molti
partecipanti: in mobile la priorita e capire stato e blocco, non vedere tutti
gli avatar contemporaneamente.

### Rischi UX

- Sovraffollamento visivo quando molti step hanno molti partecipanti.
- Troppi avatar visibili sopra la timeline.
- Confusione tra ruolo e stato se entrambi usano colori forti.
- Collisione grafica tra avatar, label step e linea timeline.
- Difficolta mobile se la timeline diventa troppo larga.
- Prestazioni e rendering pesante se ogni step apre molte immagini o tooltip.
- Ambiguita tra partecipanti generali della sottofase e partecipanti specifici dello step.

## Step 30L-26 – Gestione aggiunta/eliminazione step timeline

Questo step e di progettazione architetturale. Non introduce modifiche a
codice, database, schema Access, endpoint o frontend.

### Obiettivo

Definire il comportamento definitivo della timeline operativa relativamente a:

- inserimento step;
- eliminazione step;
- riordino step;
- storico;
- audit;
- impatto sui partecipanti;
- impatto sul documento.

La timeline resta orizzontale, sequenziale, ordinata e bloccante.

### Inserimento step

Gli step possono essere inseriti:

- prima del primo step;
- tra due step esistenti;
- dopo l'ultimo step.

Regole consigliate:

| Caso | Regola |
| --- | --- |
| Inserimento prima del primo step | Consentito solo se nessuno step e completato; altrimenti rischia di alterare il significato storico del percorso gia avviato. |
| Inserimento tra due step | Consentito se il punto di inserimento e dopo step non completati o prima della parte ancora non eseguita della timeline. |
| Inserimento dopo l'ultimo step | Sempre consentito se la sottofase non e chiusa; lo step entra in coda e partecipa al blocco sequenziale. |
| Ricalcolo `Ordine` | Deve essere deterministico e non distruttivo; preferibile usare gap tra ordini o ricalcolo controllato in transazione. |
| Effetto sullo step attivo | Dopo l'inserimento lo step attivo va ricalcolato come primo step non completato/non annullato della timeline. |
| Storico | L'inserimento deve essere storicizzato come evento di timeline. |

Principio: uno step inserito entra subito nella sequenza bloccante. Se viene
inserito prima di step non ancora completati, puo diventare il nuovo step
attivo.

### Eliminazione step

L'eliminazione fisica e rischiosa perche puo cancellare il significato storico
della timeline. La scelta consigliata e:

```text
eliminazione fisica solo per step mai iniziati, senza partecipanti, documenti, allegati o note;
annullamento logico in tutti gli altri casi.
```

Valutazione per stato/contenuto:

| Caso | Regola consigliata |
| --- | --- |
| Step non iniziato | Eliminabile fisicamente solo se non ha partecipanti, documenti, allegati o note. |
| Step attivo | Non eliminabile fisicamente; consentire solo annullamento controllato se non ha azioni sostanziali. |
| Step completato | Non eliminabile; solo annullabile logicamente con motivazione e audit. |
| Step con partecipanti | Non eliminabile fisicamente; annullamento logico preservando partecipanti e storico. |
| Step con documento | Non eliminabile fisicamente; documento e collegamento devono restare tracciabili. |
| Step con allegati | Non eliminabile fisicamente; allegati e storico devono restare consultabili. |
| Step con note | Non eliminabile fisicamente; note da preservare come memoria operativa. |

Vantaggi annullamento logico:

- preserva storico;
- evita perdita di documenti e partecipanti;
- mantiene audit;
- riduce rischi di incoerenza nella timeline.

Rischi annullamento logico:

- la UI deve distinguere chiaramente step annullati da step bloccati;
- il calcolo dello step attivo deve sapere se `CANCELLED` blocca o no;
- possono accumularsi step annullati, richiedendo filtri o vista storico.

### Riordino step

Il riordino futuro puo essere realizzato con drag and drop, ma deve essere
controllato.

Regole consigliate:

| Tema | Regola |
| --- | --- |
| Step completati | Non spostabili. |
| Step annullati | Non spostabili nella timeline operativa; restano nello storico. |
| Step attivo | Spostabile solo se non ha partecipanti, documenti, allegati o note; in caso contrario non spostabile. |
| Step futuri non iniziati | Spostabili se non rompono vincoli di step standard protetti. |
| Partecipanti | Restano collegati allo step spostato. |
| Stato | Lo stato resta collegato allo step; dopo il riordino si ricalcola `ACTIVE`/`LOCKED`. |
| Storico | Ogni riordino deve essere storicizzato con ordine precedente e nuovo ordine. |

Il riordino non deve mai produrre una timeline in cui uno step completato
risulti successivo a uno step che dipendeva logicamente dal suo completamento.

### Step standard

Step standard:

- `REDIGI`;
- `REVISIONA`;
- `FIRMA`;
- `PROTOCOLLA`.

Scelta consigliata:

```text
gli step standard non sono tutti obbligatori in assoluto, ma sono protetti quando generati da template o gia usati.
```

Regole:

| Step standard | Regola |
| --- | --- |
| Non ancora iniziato e non vincolato | Puo essere annullato o rimosso se il tipo procedimento lo consente. |
| Gia completato | Non eliminabile e non spostabile. |
| Con partecipanti/documenti/note | Non eliminabile fisicamente. |
| Richiesto dal template procedimento | Non eliminabile; eventualmente annullabile solo con motivazione. |

Questa scelta conserva flessibilita senza trasformare la timeline in una lista
arbitraria priva di garanzie.

### Step personalizzati

Step personalizzati iniziali:

- `CHIAMATA`;
- `EMAIL`;
- `APPUNTAMENTO`;
- `PARERE`;
- `SOPRALLUOGO`;
- `ALTRO`.

Regole:

- devono avere tipo step esplicito;
- possono essere configurabili in futuro da catalogo;
- partecipano al blocco sequenziale come gli step standard;
- possono avere partecipanti, note, documento collegato e allegati;
- se completati o collegati a contenuti non vanno eliminati fisicamente.

### Storico e audit

La timeline deve essere storicizzabile. Eventi da auditare:

- aggiunta step;
- eliminazione fisica consentita;
- annullamento logico;
- riordino step;
- cambio stato;
- cambio data prevista;
- collegamento/scollegamento partecipanti;
- collegamento documento o allegati;
- modifica note.

Esigenze future:

| Tema | Esigenza |
| --- | --- |
| Audit utente | Tracciare chi ha eseguito l'operazione. |
| Audit data | Tracciare quando e stata eseguita. |
| Stato precedente | Conservare prima/dopo per riordino, stato e contenuti sensibili. |
| Motivazione | Obbligatoria per annullamento di step completati o con contenuti. |
| Ripristino | Valutare ripristino logico per step annullati. |

### Impatto sui partecipanti

| Operazione | Effetto sui partecipanti collegati allo step |
| --- | --- |
| Eliminazione fisica consentita | Ammessa solo se non ci sono partecipanti collegati. |
| Annullamento step | Partecipanti restano collegati come storico; non devono piu bloccare la timeline. |
| Riordino step | Partecipanti seguono lo step. |
| Cambio stato step | Puo aggiornare stati visuali ma non deve sovrascrivere automaticamente stati partecipante senza regola dedicata. |

Se un partecipante e generale della sottofase, non deve essere alterato da
eliminazione, annullamento o riordino di uno step specifico.

### Impatto sul documento

| Elemento | Regola |
| --- | --- |
| Documento principale | Non viene eliminato se uno step viene eliminato o annullato. |
| Versioni | Restano nello storico documentale. |
| Documento collegato allo step | Blocca eliminazione fisica dello step; lo step puo solo essere annullato logicamente. |
| Allegati | Bloccano eliminazione fisica; restano consultabili nello storico. |
| Note documentali | Devono restare tracciabili se collegate allo step. |

Principio: la timeline puo cambiare, ma non deve cancellare la memoria
documentale del procedimento.

### Regole definitive consigliate

1. Step completati non eliminabili fisicamente.
2. Step completati non riordinabili.
3. Step attivo non eliminabile fisicamente.
4. Step con partecipanti non eliminabile fisicamente.
5. Step con documento o allegati non eliminabile fisicamente.
6. Step con note non eliminabile fisicamente.
7. Riordino consentito solo su step non completati e privi di vincoli sostanziali.
8. Gli step standard sono protetti se richiesti dal template, completati o collegati a contenuti.
9. Gli step personalizzati partecipano al blocco sequenziale come gli standard.
10. L'annullamento logico e la scelta predefinita quando esiste qualunque traccia operativa.
11. Ogni aggiunta, annullamento, eliminazione consentita, riordino e cambio stato deve essere auditabile.
12. Dopo ogni modifica strutturale va ricalcolato lo step attivo.

### UI futura

Timeline orizzontale con punto di inserimento tra due step:

```text
REDIGI --- [+] --- REVISIONA --- [+] --- FIRMA --- [+] --- PROTOCOLLA
```

Ogni step avra un menu contestuale:

- Modifica;
- Inserisci prima;
- Inserisci dopo;
- Annulla;
- Elimina;
- Gestisci partecipanti.

Regole UI:

- mostrare `Elimina` solo quando l'eliminazione fisica e consentita;
- mostrare `Annulla` quando lo step non e eliminabile ma puo essere escluso dal percorso;
- disabilitare azioni non permesse spiegandone il motivo;
- evidenziare se uno step ha partecipanti, documenti, allegati o note;
- dopo inserimento/riordino mostrare la timeline ricalcolata.

### Rischi architetturali

- Eliminazione fisica usata dove serve annullamento logico.
- Riordino che rompe il significato sequenziale e bloccante.
- Perdita di partecipanti collegati allo step.
- Perdita o oscuramento di documenti, allegati e note.
- Mancanza di audit su modifiche strutturali.
- UI troppo permissiva rispetto alle regole di dominio.
- Accumulo di step annullati senza filtri o vista storico.

## Step 30L-27 – Partecipanti collegati allo step

Questo step introduce il modello ibrido dei partecipanti della sottofase: un
partecipante puo essere generale della sottofase oppure collegato a uno
specifico step della timeline.

### Modello dati

Tabella esistente: `T_SottofasePartecipanti`.

Campo aggiunto:

- `IDStepOperativo LONG NULL`.

Significato:

- `IDStepOperativo = NULL`: partecipante generale della sottofase;
- `IDStepOperativo` valorizzato: partecipante collegato a uno specifico step
  timeline in `T_SottofaseStepOperativi`.

Indice aggiunto:

- `IX_T_SottofasePartecipanti_IDStepOperativo`.

Backup Access creato prima della modifica schema:

```text
C:\Users\fintu\CloudVVF\Documents\Sviluppo\Grisu\Backup\ProtocolloMonitor_BACKUP_20260601_124025.accdb
```

Esito schema:

- tabella `T_SottofasePartecipanti` gia esistente;
- campo `IDStepOperativo` aggiunto;
- indice `IX_T_SottofasePartecipanti_IDStepOperativo` creato;
- nessun dato reale popolato automaticamente.

### Backend

File modificati:

- `backend/schemas/sottofase_partecipanti.py`;
- `backend/repositories/sottofase_partecipanti_repository.py`;
- `backend/services/sottofase_partecipanti_service.py`;
- `backend/api/routes/protocollo_monitor.py`;
- `tests/test_sottofase_partecipanti_repository.py`;
- `tests/test_sottofase_partecipanti_service.py`;
- `tests/test_sottofase_partecipanti_endpoint.py`;
- `ROADMAP_PROTOCOLLOMONITOR.md`.

File creati: nessuno.

Endpoint modificati:

| Metodo | Endpoint | Modifica |
| --- | --- | --- |
| `GET` | `/protocollo-monitor/sottofasi/{id_sottofase}/partecipanti` | Restituisce anche `id_step_operativo`. |
| `POST` | `/protocollo-monitor/sottofasi/{id_sottofase}/partecipanti` | Accetta opzionalmente `idStepOperativo`. |

Endpoint aggiunto:

| Metodo | Endpoint | Scopo |
| --- | --- | --- |
| `GET` | `/protocollo-monitor/sottofasi/{id_sottofase}/step-operativi/{id_step}/partecipanti` | Restituisce partecipanti collegati a uno specifico step timeline. |

### Validazioni implementate

- Se `idStepOperativo` e valorizzato, lo step deve esistere in
  `T_SottofaseStepOperativi`.
- Lo step deve appartenere alla stessa `IDSottofase`.
- Ruolo coerente con il codice step quando determinabile:
  - `REVISIONA` -> `REVISORE`;
  - `FIRMA` -> `FIRMATARIO`;
  - `PROTOCOLLA` -> `PROTOCOLLATORE`.
- Approccio scelto per ruolo incoerente: errore `400`, non warning.
- Duplicato partecipante generale: stessa sottofase, email e ruolo con
  `IDStepOperativo NULL`.
- Duplicato partecipante step: stessa sottofase, stesso `IDStepOperativo`,
  stessa email e stesso ruolo.
- Backup Access prima dell'insert.
- Insert transazionale con rollback su errore.

### Test

Test aggiornati o aggiunti per:

- campo `IDStepOperativo` aggiunto se assente;
- indice `IX_T_SottofasePartecipanti_IDStepOperativo` creato se assente;
- POST partecipante generale con `idStepOperativo` nullo;
- POST partecipante collegato a step valido;
- POST `idStepOperativo` inesistente;
- POST `idStepOperativo` appartenente ad altra sottofase;
- ruoli coerenti `REVISORE`/`REVISIONA`, `FIRMATARIO`/`FIRMA`,
  `PROTOCOLLATORE`/`PROTOCOLLA`;
- ruolo incoerente con errore;
- duplicato generale;
- duplicato su step;
- GET con `id_step_operativo`;
- rollback su errore insert.

Risultato test mirati:

```text
33 passed
```

### Vincoli rispettati

- `Python/server_protocollo.py` non modificato.
- Frontend non modificato.
- Workflow legacy non modificato.
- PostgreSQL-friendly: chiave opzionale, semantica esplicita, nessuna logica
  Access-only nel contratto.
- Nessun commit eseguito.

### Punti dubbi

- Il campo si chiama `IDStepOperativo`, mentre la chiave primaria della tabella
  step e `IDStepSottofase`; il nome e coerente semanticamente con la timeline,
  ma va documentato nella futura migrazione PostgreSQL.
- La coerenza ruolo-step oggi copre solo step standard noti; per step
  personalizzati servira una configurazione futura.
- Il vincolo referenziale non e stato introdotto come FK Access: la coerenza e
  garantita dal backend.

## 14. Prossima tabella di marcia

| Prossimo step | Obiettivo | Note prudenziali |
| --- | --- | --- |
| Step 30L-28 | Completamento automatico guidato dai partecipanti. | Definire quorum, obbligatorieta, respingimenti e richieste integrazione prima delle automazioni. |
| Step 30L-29 | Audit e storico timeline. | Progettare eventi di audit prima di attivare modifiche strutturali reali. |
| Step 30L-30 | Implementazione UI timeline dinamica. | Tradurre regole di inserimento, annullamento e riordino in controlli frontend sicuri. |

## 15. Punti non ricostruibili automaticamente

Alcuni elementi non sono completamente ricostruibili dai soli file senza
interrogare il database reale o recuperare tutta la cronologia conversazionale:

- elenco completo dei backup creati nelle prove reali precedenti;
- stato attuale di ogni record Access dopo test manuali;
- eventuali dati inseriti manualmente fuori dal codice;
- conferma visuale browser per ogni step UI;
- mapping completo di tabelle Access legacy non usate direttamente dai repository.

## 16. Regole per mantenere aggiornata questa roadmap

1. Aggiornare il documento alla fine di ogni milestone.
2. Aggiungere sempre endpoint nuovi nella tabella API.
3. Aggiungere sempre campi/tabelle nuove nelle sezioni dati.
4. Annotare commit Git associato allo step.
5. Indicare numero test passato dopo `pytest`.
6. Annotare backup reale creato solo se lo step esegue scritture Access.
7. Separare chiaramente cio che e read-only da cio che scrive.
8. Evidenziare ogni modifica a `Python/server_protocollo.py`, se mai avverra.
9. Non rimuovere decisioni architetturali storiche: aggiungere note di superamento.
10. Mantenere la roadmap come fonte per aprire nuove chat operative.
