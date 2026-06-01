# Trust Signer API discovery

## Obiettivo

Questo documento raccoglie le evidenze iniziali sulle API osservate di Trust Signer e propone un metodo controllato per completare la mappatura dei flussi utili a una eventuale integrazione con SoluzioniOperative / ProtocolloMonitor.

Vincoli operativi per questa fase:

- non usare token reali;
- non salvare credenziali;
- non modificare database;
- non eseguire chiamate operative di firma;
- non assumere che le API osservate siano pubbliche o autorizzate all'uso server-to-server.

Base URL osservata:

```text
https://trustsigner.tipki.it/ITTCryptoClientWeb/rest/api/
```

## 1. Endpoint gia individuati

| Endpoint | Metodo | Stato osservazione | Dati osservati |
| --- | --- | --- | --- |
| `/configuration/init` | `GET` | individuato | versione, licenza, vincoli upload, `activeVerification`, `signatureReasons` |
| `/files/list` | `GET` | individuato | elenco dei file presenti nella sessione o area temporanea |
| `/files/upload` | `POST` | individuato | `uploadedFiles` con `id`, `type`, `signed`, `size` |
| `/signature/fds/certificates/{signer_id}` | `GET` | individuato | certificati disponibili per il firmatario |
| `/signature/build-image` | `POST` | individuato | generazione o preparazione immagine grafica di firma |

Signer ID osservato:

```text
MTRFNC72M26A176S
```

Nota: il valore osservato sembra un identificativo personale o fiscale. Non deve essere riutilizzato in ambienti diversi da quelli autorizzati e non deve essere salvato in configurazioni applicative.

## 2. Probabile funzione di ciascun endpoint

### `GET /configuration/init`

Probabile endpoint di bootstrap della web application. Sembra restituire parametri funzionali e limiti operativi necessari al client prima di consentire upload, verifica o firma.

Elementi rilevanti da confermare:

- versione del client web o del backend;
- tipo e stato licenza;
- limiti di upload, formati ammessi e dimensione massima;
- disponibilita della verifica firma tramite `activeVerification`;
- causali disponibili tramite `signatureReasons`.

Possibile utilita per ProtocolloMonitor: leggere vincoli e funzionalita disponibili prima di proporre un flusso assistito all'utente.

### `GET /files/list`

Probabile elenco dei file caricati nella sessione Trust Signer o in un contenitore temporaneo associato al browser.

Elementi da osservare:

- se l'elenco dipende da cookie/sessione;
- se i file hanno scadenza;
- se sono presenti metadati come nome originale, tipo MIME, hash, stato firma o stato verifica;
- se l'endpoint restituisce anche file firmati generati dopo il processo.

Possibile utilita per ProtocolloMonitor: monitorare i file gestiti durante una integrazione assistita, solo se autorizzato e documentato.

### `POST /files/upload`

Probabile endpoint di caricamento documenti. La risposta osservata include `uploadedFiles` con identificativi interni.

Elementi da osservare:

- formato della richiesta, probabilmente `multipart/form-data`;
- nome del campo file;
- eventuali parametri aggiuntivi richiesti per PDF, P7M, XML;
- relazione tra `id` restituito e successive chiamate di firma;
- gestione errori su formato non ammesso o dimensione eccessiva.

Possibile utilita per ProtocolloMonitor: inviare documenti da firmare o verificare, ma solo in un'integrazione autorizzata. Nella fase attuale l'upload deve restare manuale o non operativo.

### `GET /signature/fds/certificates/{signer_id}`

Probabile endpoint di lettura dei certificati disponibili per un firmatario. Il segmento `{signer_id}` potrebbe corrispondere a codice fiscale, identificativo utente o account remoto.

Elementi da osservare:

- struttura del certificato restituito;
- identificativo del certificato da usare nelle richieste di firma;
- scadenza, issuer, policy, uso firma;
- differenza tra firma remota, firma automatica, firma grafica o altri profili;
- requisiti di sessione o autenticazione.

Possibile utilita per ProtocolloMonitor: preselezionare o validare il certificato dell'utente, solo con consenso e documentazione del fornitore.

### `POST /signature/build-image`

Probabile endpoint per costruire l'immagine grafica della firma visibile da apporre su PDF/PAdES.

Elementi da osservare:

- payload con coordinate, pagina, testo, motivo, luogo, data;
- eventuale immagine restituita o identificativo immagine temporaneo;
- relazione con il successivo endpoint di firma PDF;
- supporto a firma invisibile o visibile.

Possibile utilita per ProtocolloMonitor: predisporre firma visibile su documenti protocollati, se il flusso PAdES viene autorizzato.

## 3. API mancanti da individuare

Le API seguenti non sono ancora state individuate con certezza e sono necessarie per valutare una vera integrazione.

| Flusso mancante | Informazioni da individuare |
| --- | --- |
| Avvio firma PDF/PAdES | endpoint, metodo HTTP, payload, riferimento file caricato, certificato, causale, tipo firma visibile/invisibile, coordinate firma |
| Avvio firma P7M/CAdES | endpoint, metodo HTTP, payload, riferimento file, certificato, formato busta, opzioni di firma |
| Avvio firma XML/XAdES | endpoint, metodo HTTP, payload, riferimento XML, profilo XAdES, eventuali namespace o trasformazioni |
| Richiesta OTP | endpoint, metodo HTTP, identificativo transazione, canale OTP, prerequisiti di autenticazione |
| Conferma OTP | endpoint, metodo HTTP, payload con OTP, transaction id, certificato e file da firmare |
| Download documento firmato | endpoint, metodo HTTP, parametro file id o signed file id, nome file, content type, gestione scadenza |
| Verifica firma | endpoint, metodo HTTP, file id o upload dedicato, report restituito, dettagli certificato e validazione temporale |
| Cancellazione file temporanei | endpoint, metodo HTTP, file id, cancellazione singola o massiva, risposta attesa |

## 4. Metodo proposto con Chrome DevTools

La mappatura deve essere eseguita manualmente con Chrome DevTools, senza salvare credenziali e senza esportare token o cookie in repository.

Procedura consigliata:

1. Aprire Trust Signer in Chrome.
2. Aprire DevTools.
3. Selezionare la scheda `Network`.
4. Attivare `Preserve log`.
5. Attivare `Disable cache`.
6. Inserire nel filtro Network:

```text
rest/api
```

7. Pulire il log Network.
8. Eseguire una singola azione UI per volta.
9. Confrontare le richieste prima e dopo il click.
10. Annotare solo struttura tecnica e nomi endpoint, evitando di copiare credenziali, token, OTP o cookie.

Azioni da testare separatamente:

- click su `Firma PDF`;
- click su `Firma P7M`;
- click su `Firma XML`;
- click su `Verifica Firma`;
- richiesta OTP;
- conferma OTP con OTP di test o ambiente non produttivo, se disponibile;
- download documento firmato;
- eliminazione o pulizia file temporanei.

Per ogni chiamata individuata annotare:

- URL completo e path relativo;
- metodo HTTP;
- query string;
- request headers rilevanti non sensibili;
- content type;
- schema del payload, oscurando valori personali;
- status code;
- schema della risposta, oscurando valori personali;
- dipendenza da cookie/sessione;
- eventuale ordine obbligatorio delle chiamate.

## 5. Valutazione preliminare per SoluzioniOperative

Le API osservate suggeriscono che Trust Signer espone un backend REST usato dal client web. Questo rende tecnicamente plausibile una integrazione, almeno per una fase assistita in cui ProtocolloMonitor prepara il documento e guida l'utente verso Trust Signer.

La possibilita di una integrazione diretta non e ancora dimostrata. Mancano gli endpoint centrali di firma, OTP, download e verifica, e non e chiaro se il servizio consenta l'uso da applicazioni terze. Inoltre, la presenza di sessione browser, cookie, vincoli CORS e licenza potrebbe limitare l'uso delle API al solo client web ufficiale.

Valutazione iniziale:

- integrazione assistita: fattibile come primo passo, con basso rischio tecnico;
- integrazione semi-automatica tramite browser o passaggio file: da valutare con attenzione, evitando automazioni non autorizzate;
- integrazione backend-to-backend: da considerare solo con documentazione ufficiale, autorizzazione del fornitore e ambiente di test dedicato.

## 6. Rischi

### API interne non documentate

Gli endpoint osservati potrebbero essere API interne del client web, non destinate a integrazioni esterne. L'uso diretto senza accordo potrebbe violare condizioni contrattuali o produrre malfunzionamenti non supportati.

### Sessione e cookie

Le chiamate potrebbero dipendere da sessione browser, cookie HttpOnly, CSRF token o autenticazione interattiva. Questo renderebbe fragile o non appropriato un uso server-side da ProtocolloMonitor.

### CORS

Anche se gli endpoint sono REST, il browser potrebbe impedire chiamate dirette dal frontend di ProtocolloMonitor se Trust Signer non abilita le origini necessarie.

### Licenza

La risposta di configurazione include dati di licenza. Occorre verificare se la licenza corrente consente integrazioni applicative, automazioni, uso multiutente o uso tramite sistemi terzi.

### Uso non autorizzato

Flussi di firma digitale e OTP hanno valore legale e richiedono consenso esplicito, tracciabilita e uso conforme. Non devono essere automatizzati senza autorizzazione formale.

### Variazioni future degli endpoint

Endpoint interni possono cambiare senza preavviso. Una integrazione basata solo su reverse engineering avrebbe costi di manutenzione alti e rischio di interruzione.

## 7. Raccomandazione architetturale

### Fase 1: integrazione assistita

ProtocolloMonitor prepara il documento e i metadati necessari, poi assiste l'utente nel flusso Trust Signer senza eseguire firme in modo automatico.

Possibili funzioni:

- apertura cartella o documento pronto alla firma;
- checklist operativa;
- registrazione manuale dell'esito firma;
- import del documento firmato dopo download manuale;
- verifica interna dello stato documento in ProtocolloMonitor senza chiamate operative a Trust Signer.

### Fase 2: studio API

Completare la mappatura tramite DevTools in ambiente autorizzato, preferibilmente con account di test e documenti non sensibili.

Deliverable consigliati:

- tabella endpoint completa;
- sequence diagram dei flussi PDF/PAdES, P7M/CAdES, XML/XAdES;
- schema dei payload oscurato;
- requisiti di autenticazione/sessione;
- punti in cui interviene OTP;
- modalita download;
- errori e retry;
- vincoli licenza.

### Fase 3: integrazione solo se autorizzata/documentata

Procedere con integrazione diretta solo se il fornitore conferma l'uso delle API e fornisce documentazione o contratto tecnico.

Requisiti minimi:

- documentazione ufficiale API;
- ambiente di test;
- credenziali tecniche dedicate;
- regole di conservazione log e audit;
- gestione sicura OTP o firma remota;
- autorizzazione CORS o canale server-to-server;
- piano di manutenzione e versionamento endpoint.

## Prossimi test manuali

1. Ripetere il bootstrap e confermare il contenuto di `/configuration/init`.
2. Caricare un PDF non sensibile e annotare payload e risposta di `/files/upload`.
3. Avviare `Firma PDF` senza completare la firma, annotando gli endpoint fino alla richiesta OTP.
4. Ripetere per `Firma P7M`.
5. Ripetere per `Firma XML`.
6. Aprire `Verifica Firma` con file non sensibile e annotare endpoint e report.
7. Individuare endpoint di download del file firmato usando un documento di test.
8. Verificare se esiste un endpoint di cancellazione file temporanei o se la pulizia e automatica.
9. Separare chiaramente dati tecnici da dati personali o credenziali.
10. Richiedere al fornitore conferma su licenza, documentazione e uso autorizzato delle API.
