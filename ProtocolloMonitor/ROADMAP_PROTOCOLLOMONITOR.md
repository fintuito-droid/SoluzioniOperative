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
| `GET` | `/protocollo-monitor/sottofasi/{id_sottofase}/workflow` | Workflow operativo REDIGI/FINE. | Read-only | `SottofaseWorkflowService`, `SottofaseDocumentaleService`. | Attivo. |
| `POST` | `/protocollo-monitor/sottofasi/{id_sottofase}/workflow/azioni` | Avanza workflow sottofase. | Scrittura controllata | `SottofaseWorkflowCommandService`, `SottofaseWorkflowActionRepository`, backup Access. | Attivo. |
| `POST` | `http://127.0.0.1:8020/open-word` | Helper locale separato per aprire `.docx` con Word da `idDocumento`. | Read-only locale/filesystem | `Python/open_word_helper.py`, Access read-only, whitelist `DocumentiWorkflow`. | Attivo Step 30L-19, fuori dal backend principale. |

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

## 14. Prossima tabella di marcia

| Prossimo step | Obiettivo | Note prudenziali |
| --- | --- | --- |
| Step 30L-20 | Firma/protocollazione documentale. | Non confondere firma operativa con firma digitale reale. |
| Step 30L-21 | Audit storico applicativo. | Introdurre tabella/eventi o logging persistente prima della multiutenza. |
| Step 30L-22 | Utente reale/login. | Sostituire `Francesco Matranga` hardcoded/provvisorio con identita autenticata. |
| Step 30L-23 | Permessi ruoli/azioni. | Rendere azioni workflow abilitate in base a ruolo/capability. |
| Step 30L-24 | Migrazione PostgreSQL preparatoria. | Mappare Access -> PostgreSQL, definire migration plan e test di parita. |
| Step 30L-25 | Hardening storage documentale. | Radici autorizzate, UNC, antivirus/OneDrive, path traversal, policy download. |
| Step 30L-26 | Workflow template. | Generare fasi/sottofasi da tipologia procedimento. |

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
