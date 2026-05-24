"""Logging strutturato backend per ProtocolloMonitor.

SCOPO DEL FILE
==============
Questo file introduce un piccolo sistema di logging strutturato, basato solo
sulla standard library Python, da riusare gradualmente in FastAPI, nel server
Flask legacy e nei futuri Repository/Service.

RESPONSABILITA
==============
- Creare logger Python configurati in modo prevedibile.
- Scrivere eventi con campi standard e sempre nello stesso ordine.
- Rendere i log leggibili nella console Windows.
- Evitare dipendenze pesanti o formatter esterni in questa fase iniziale.
- Offrire funzioni semplici: `get_logger`, `log_event`, `log_error`,
  `log_operation_start`, `log_operation_end`.

MOTIVAZIONE ARCHITETTURALE
==========================
ProtocolloMonitor sta iniziando la modernizzazione verso una piattaforma
multi modulo chiamata Soluzioni Operative. Il logging deve quindi nascere come
capacita trasversale, non come dettaglio di una singola route FastAPI o di un
singolo script Flask.

Questo modulo non viene ancora collegato ai file runtime esistenti. La scelta
e intenzionale: Step 1, Attivita 3 deve aggiungere la capacita tecnica senza
cambiare endpoint, query, salvataggi Access, frontend Vue/Vuetify o flusso
Grisu.

VINCOLI
=======
- Usare solo standard library Python.
- Non modificare il comportamento applicativo esistente.
- Non introdurre logging automatico dentro FastAPI, Flask legacy o script
  Access durante questa attivita.
- Non registrare dati sensibili non necessari.
- Mantenere un formato adatto alla console Windows: testo lineare key=value,
  senza dipendere da colori, terminali avanzati o caratteri speciali.

COMPATIBILITA ACCESS
====================
Access resta il database operativo corrente. Questo modulo non apre
connessioni, non esegue query e non conosce `pyodbc`. Quando i futuri
Repository Access useranno questi helper, potranno loggare operazioni come
lettura protocollo, salvataggio documento o errore connessione senza cambiare
la logica dati.

PREPARAZIONE POSTGRESQL
=======================
PostgreSQL e il target definitivo. I campi standard includono `module`,
`operation`, `entity_type`, `entity_id`, `user_id`, `request_id`, `status` e
`duration_ms` perche sono utili sia nei log testuali sia in un futuro audit
applicativo persistente su PostgreSQL.

PUNTI DI ATTENZIONE
===================
- Il logger non deve duplicare righe se chiamato piu volte: `get_logger`
  configura un handler solo quando necessario.
- I valori `None` vengono serializzati come stringa vuota controllata, cosi le
  chiavi restano sempre presenti e facili da cercare.
- Le eccezioni possono essere registrate senza esporre traceback completi se
  non richiesto dal chiamante.

NOTE FUTURA EVOLUZIONE
======================
- In Step successivi il modulo potra essere collegato a middleware FastAPI.
- Potra ricevere `request_id` da header HTTP o generarlo per richiesta.
- Potra alimentare un `audit_service` separato, senza confondere log tecnico e
  audit applicativo.
- Potra essere esteso con output JSON puro se la piattaforma verra eseguita in
  container o servizi centralizzati di log collection.
"""

from __future__ import annotations

from datetime import datetime, timezone
import logging as python_logging
from time import perf_counter
from traceback import format_exception_only
from typing import Any


DEFAULT_LOGGER_NAME = "protocollo_monitor"
DEFAULT_MODULE = "PROTOCOLLO_MONITOR"
DEFAULT_STATUS = "ok"


STANDARD_FIELDS = (
    "timestamp",
    "level",
    "module",
    "operation",
    "entity_type",
    "entity_id",
    "user_id",
    "request_id",
    "status",
    "duration_ms",
    "message",
)


def get_logger(name: str = DEFAULT_LOGGER_NAME) -> python_logging.Logger:
    """Restituisce un logger applicativo configurato per log strutturati.

    Cosa fa:
    crea o recupera un logger standard Python con un `StreamHandler` minimale.
    Il formatter stampa solo il messaggio perche `log_event` costruisce gia una
    riga completa con tutti i campi standard.

    Perche esiste:
    Repository, Service, route FastAPI e script Flask legacy devono poter usare
    lo stesso logger senza ricreare handler diversi o produrre righe duplicate.

    Parametri:
    - `name`: nome del logger Python. Il default identifica l'intero modulo
      ProtocolloMonitor dentro la futura piattaforma Soluzioni Operative.

    Valori restituiti:
    - un'istanza `logging.Logger` pronta a scrivere in console.

    Rischi evitati:
    - duplicazione degli handler quando il modulo viene importato piu volte;
    - formato console diverso tra FastAPI, Flask legacy e script;
    - introduzione di dipendenze esterne non necessarie.

    Uso futuro:
    i Service potranno chiamare `get_logger()` una volta e poi passarlo a
    `log_event` / `log_error` durante operazioni di dominio. I Repository
    potranno fare lo stesso quando eseguono query Access o PostgreSQL.
    """

    logger = python_logging.getLogger(name)
    logger.setLevel(python_logging.INFO)
    logger.propagate = False

    if not logger.handlers:
        handler = python_logging.StreamHandler()
        handler.setFormatter(python_logging.Formatter("%(message)s"))
        logger.addHandler(handler)

    return logger


def _utc_timestamp() -> str:
    """Produce un timestamp UTC ISO-8601 stabile per ogni evento.

    Cosa fa:
    restituisce la data/ora corrente in UTC con precisione al secondo.

    Perche esiste:
    usare una sola funzione evita formati diversi tra chiamanti e prepara i log
    a essere correlati in ambienti futuri multiutente o multi modulo.

    Parametri:
    nessuno.

    Valori restituiti:
    - stringa ISO-8601 con suffisso `Z`.

    Rischi evitati:
    - mescolare timestamp locali e UTC;
    - dipendere dal formato predefinito del modulo `logging`;
    - rendere difficili ordinamento e ricerca nei log.

    Uso futuro:
    lo stesso formato potra essere salvato in PostgreSQL in una colonna
    `timestamptz` durante l'introduzione dell'audit persistente.
    """

    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace(
        "+00:00",
        "Z",
    )


def _normalize_value(value: Any) -> str:
    """Converte un valore arbitrario in testo sicuro per log key=value.

    Cosa fa:
    trasforma `None` in stringa vuota e sostituisce ritorni a capo, tab e spazi
    multipli con spazi singoli. Se il valore contiene spazi, virgolette o `=`,
    viene racchiuso tra virgolette con escaping minimale.

    Perche esiste:
    i log devono restare leggibili in console Windows e cercabili con strumenti
    semplici. Una riga key=value e utile solo se ogni valore resta sulla stessa
    riga e non rompe la struttura.

    Parametri:
    - `value`: qualsiasi valore proveniente da route, Service o Repository.

    Valori restituiti:
    - stringa normalizzata, pronta per essere inserita in una riga di log.

    Rischi evitati:
    - log multilinea accidentali;
    - campi mancanti quando il valore e `None`;
    - rottura del formato in presenza di spazi o uguali.

    Uso futuro:
    i Repository potranno passare ID, nomi tabella o provider DB senza
    preoccuparsi del formato finale.
    """

    if value is None:
        text = ""
    else:
        text = str(value)

    text = " ".join(text.replace("\t", " ").splitlines()).strip()

    if not text:
        return ""

    if any(character.isspace() for character in text) or "=" in text or '"' in text:
        escaped_text = text.replace("\\", "\\\\").replace('"', '\\"')
        return f'"{escaped_text}"'

    return text


def _format_event(fields: dict[str, Any]) -> str:
    """Formatta un dizionario evento secondo l'ordine standard dei campi.

    Cosa fa:
    produce una singola riga testuale con campi `key=value`, partendo sempre da
    `STANDARD_FIELDS`. Eventuali campi extra vengono aggiunti alla fine in
    ordine alfabetico per rendere stabile il risultato.

    Perche esiste:
    mantenere un ordine fisso rende i log piu facili da leggere e confrontare,
    soprattutto durante la modernizzazione dove FastAPI, Flask legacy e script
    Python potrebbero convivere per un periodo.

    Parametri:
    - `fields`: dizionario con campi standard ed eventuali metadati extra.

    Valori restituiti:
    - stringa pronta per `logger.log(...)`.

    Rischi evitati:
    - log con campi in ordine casuale;
    - dimenticare chiavi standard;
    - differenze tra log emessi da componenti diversi.

    Uso futuro:
    se si passera a JSON puro, questa funzione sara il punto piu semplice da
    sostituire senza cambiare le funzioni pubbliche.
    """

    ordered_keys = list(STANDARD_FIELDS)
    extra_keys = sorted(key for key in fields if key not in STANDARD_FIELDS)
    output_keys = ordered_keys + extra_keys

    return " ".join(
        f"{key}={_normalize_value(fields.get(key))}"
        for key in output_keys
    )


def _level_to_int(level: str | int) -> int:
    """Converte un livello testuale o numerico in livello `logging`.

    Cosa fa:
    accetta sia valori come `"INFO"` / `"ERROR"` sia costanti numeriche del
    modulo `logging`.

    Perche esiste:
    le funzioni pubbliche devono essere semplici per i futuri chiamanti. Un
    Service potra passare `"warning"` senza conoscere le costanti interne.

    Parametri:
    - `level`: livello testuale o intero.

    Valori restituiti:
    - intero compatibile con `logging.Logger.log`.

    Rischi evitati:
    - eccezioni per livelli sconosciuti;
    - differenze di maiuscole/minuscole;
    - chiamanti costretti a importare `logging`.

    Uso futuro:
    Repository e Service potranno mantenere dipendenze leggere e chiamare solo
    questo modulo.
    """

    if isinstance(level, int):
        return level

    normalized_level = str(level).strip().upper()
    return python_logging._nameToLevel.get(normalized_level, python_logging.INFO)


def _level_to_name(level: str | int) -> str:
    """Restituisce il nome testuale del livello log.

    Cosa fa:
    normalizza il livello in una stringa come `INFO`, `WARNING` o `ERROR`.

    Perche esiste:
    il campo standard `level` deve essere sempre leggibile anche quando il
    chiamante usa un intero.

    Parametri:
    - `level`: livello testuale o numerico.

    Valori restituiti:
    - nome del livello in maiuscolo.

    Rischi evitati:
    - valori non uniformi nel campo `level`;
    - ambiguita quando si passa un livello numerico.

    Uso futuro:
    utile per filtri in console, file log o audit tecnico.
    """

    level_value = _level_to_int(level)
    return python_logging.getLevelName(level_value)


def log_event(
    *,
    logger: python_logging.Logger | None = None,
    level: str | int = "INFO",
    module: str = DEFAULT_MODULE,
    operation: str = "",
    entity_type: str = "",
    entity_id: str | int | None = None,
    user_id: str | int | None = None,
    request_id: str | None = None,
    status: str = DEFAULT_STATUS,
    duration_ms: int | float | None = None,
    message: str = "",
    **extra_fields: Any,
) -> None:
    """Scrive un evento strutturato con tutti i campi standard.

    Cosa fa:
    costruisce una riga key=value contenente timestamp, livello, modulo,
    operazione, entita, utente, richiesta, stato, durata e messaggio. Eventuali
    campi extra vengono aggiunti in coda.

    Perche esiste:
    e il punto di ingresso principale per tutti i componenti futuri. Invece di
    chiamare direttamente `logger.info("testo libero")`, route, Service e
    Repository potranno produrre log coerenti e cercabili.

    Parametri:
    - `logger`: logger Python opzionale; se assente viene usato il default.
    - `level`: livello log testuale o numerico.
    - `module`: codice modulo, oggi `PROTOCOLLO_MONITOR`.
    - `operation`: nome breve dell'operazione, ad esempio `protocollo_list`.
    - `entity_type`: tipo entita, ad esempio `protocollo` o `documento`.
    - `entity_id`: identificativo entita quando disponibile.
    - `user_id`: utente corrente quando disponibile.
    - `request_id`: identificativo richiesta quando disponibile.
    - `status`: esito sintetico, ad esempio `ok`, `error`, `start`.
    - `duration_ms`: durata operazione in millisecondi, se nota.
    - `message`: descrizione leggibile.
    - `extra_fields`: metadati aggiuntivi controllati dal chiamante.

    Valori restituiti:
    nessuno. La funzione produce un effetto intenzionale: scrive su logger.

    Rischi evitati:
    - log testuali non uniformi;
    - perdita di campi utili per debug e audit futuro;
    - dipendenza dei Service dal formato console.

    Uso futuro:
    i Service useranno questa funzione per eventi di dominio; i Repository per
    eventi tecnici come query, provider usato o errore connessione.
    """

    active_logger = logger or get_logger()

    event_fields: dict[str, Any] = {
        "timestamp": _utc_timestamp(),
        "level": _level_to_name(level),
        "module": module,
        "operation": operation,
        "entity_type": entity_type,
        "entity_id": entity_id,
        "user_id": user_id,
        "request_id": request_id,
        "status": status,
        "duration_ms": duration_ms,
        "message": message,
    }
    event_fields.update(extra_fields)

    active_logger.log(_level_to_int(level), _format_event(event_fields))


def log_error(
    *,
    logger: python_logging.Logger | None = None,
    module: str = DEFAULT_MODULE,
    operation: str = "",
    entity_type: str = "",
    entity_id: str | int | None = None,
    user_id: str | int | None = None,
    request_id: str | None = None,
    duration_ms: int | float | None = None,
    message: str = "",
    error: BaseException | None = None,
    include_exception_type: bool = True,
    **extra_fields: Any,
) -> None:
    """Scrive un evento di errore strutturato.

    Cosa fa:
    prepara un log con livello `ERROR` e status `error`. Se riceve un'eccezione,
    aggiunge campi extra con tipo errore e descrizione sintetica.

    Perche esiste:
    gli errori nei futuri Service/Repository devono essere diagnosticabili
    senza spargere `try/except` con messaggi liberi e diversi in ogni file.

    Parametri:
    - stessi campi principali di `log_event`;
    - `error`: eccezione Python opzionale;
    - `include_exception_type`: abilita il campo `error_type`;
    - `extra_fields`: ulteriori dati di contesto non sensibili.

    Valori restituiti:
    nessuno. Scrive un evento sul logger configurato.

    Rischi evitati:
    - perdita del tipo eccezione;
    - log multilinea difficili da leggere;
    - esposizione accidentale di traceback completi quando non necessari.

    Uso futuro:
    un Repository Access potra loggare un errore `pyodbc` senza decidere il
    formato; un Service potra aggiungere `entity_id` e `operation`.
    """

    if error is not None:
        if include_exception_type:
            extra_fields.setdefault("error_type", error.__class__.__name__)

        error_message = "".join(
            format_exception_only(error.__class__, error)
        ).strip()
        extra_fields.setdefault("error_message", error_message)

    log_event(
        logger=logger,
        level="ERROR",
        module=module,
        operation=operation,
        entity_type=entity_type,
        entity_id=entity_id,
        user_id=user_id,
        request_id=request_id,
        status="error",
        duration_ms=duration_ms,
        message=message,
        **extra_fields,
    )


def log_operation_start(
    *,
    logger: python_logging.Logger | None = None,
    module: str = DEFAULT_MODULE,
    operation: str,
    entity_type: str = "",
    entity_id: str | int | None = None,
    user_id: str | int | None = None,
    request_id: str | None = None,
    message: str = "Operazione avviata",
    **extra_fields: Any,
) -> float:
    """Registra l'inizio di un'operazione e restituisce il marker temporale.

    Cosa fa:
    emette un evento con status `start` e restituisce il valore di
    `perf_counter()`, da passare poi a `log_operation_end`.

    Perche esiste:
    molte operazioni future avranno bisogno di misurare durata: query Access,
    query PostgreSQL, salvataggi PDF, chiamate JasperReports, workflow e
    notifiche. Questa funzione offre un modo uniforme e leggero per farlo.

    Parametri:
    - campi principali di contesto;
    - `operation`: obbligatoria per identificare cosa sta iniziando;
    - `message`: testo leggibile, default conservativo;
    - `extra_fields`: dati aggiuntivi non sensibili.

    Valori restituiti:
    - float prodotto da `perf_counter`, adatto al calcolo durata.

    Rischi evitati:
    - usare `datetime` per misurare durate;
    - formati diversi per eventi di start;
    - perdita del contesto request/user/entity.

    Uso futuro:
    un Service potra fare `started_at = log_operation_start(...)` prima di
    chiamare un Repository e poi `log_operation_end(started_at=started_at, ...)`.
    """

    started_at = perf_counter()

    log_event(
        logger=logger,
        level="INFO",
        module=module,
        operation=operation,
        entity_type=entity_type,
        entity_id=entity_id,
        user_id=user_id,
        request_id=request_id,
        status="start",
        duration_ms=0,
        message=message,
        **extra_fields,
    )

    return started_at


def log_operation_end(
    *,
    started_at: float | None = None,
    logger: python_logging.Logger | None = None,
    module: str = DEFAULT_MODULE,
    operation: str,
    entity_type: str = "",
    entity_id: str | int | None = None,
    user_id: str | int | None = None,
    request_id: str | None = None,
    status: str = DEFAULT_STATUS,
    message: str = "Operazione completata",
    **extra_fields: Any,
) -> None:
    """Registra la fine di un'operazione con durata calcolata.

    Cosa fa:
    calcola `duration_ms` partendo dal marker restituito da
    `log_operation_start`. Se il marker non viene fornito, la durata resta
    vuota ma il log viene comunque scritto.

    Perche esiste:
    separare start/end rende semplice misurare operazioni lente senza inserire
    logica temporale in ogni Service o Repository.

    Parametri:
    - `started_at`: marker `perf_counter` opzionale;
    - campi principali di contesto;
    - `status`: esito finale, default `ok`;
    - `message`: testo leggibile;
    - `extra_fields`: dati aggiuntivi non sensibili.

    Valori restituiti:
    nessuno. Scrive un evento strutturato.

    Rischi evitati:
    - calcoli durata duplicati e incoerenti;
    - assenza di durata nelle operazioni critiche;
    - log di fine operazione non correlabili allo start.

    Uso futuro:
    utile per endpoint FastAPI, operazioni Flask legacy, Repository Access e
    Repository PostgreSQL.
    """

    duration_ms: int | None = None

    if started_at is not None:
        duration_ms = int((perf_counter() - started_at) * 1000)

    log_event(
        logger=logger,
        level="INFO" if status == DEFAULT_STATUS else "WARNING",
        module=module,
        operation=operation,
        entity_type=entity_type,
        entity_id=entity_id,
        user_id=user_id,
        request_id=request_id,
        status=status,
        duration_ms=duration_ms,
        message=message,
        **extra_fields,
    )
