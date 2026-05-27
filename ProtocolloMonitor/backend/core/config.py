"""Configurazione centralizzata di ProtocolloMonitor.

Questo modulo introduce la prima fondazione tecnica dello Step 1 di
modernizzazione, ma NON cambia ancora il comportamento applicativo.

Le route FastAPI, il server Flask legacy e gli script di salvataggio Access
continuano a usare i valori hardcoded esistenti finche non verra implementata
un'attivita successiva di integrazione. In questa fase il modulo serve come
fonte canonica pronta all'uso, con default identici ai valori operativi attuali.

Perche questa configurazione esiste:

1. ProtocolloMonitor e il primo modulo operativo della futura piattaforma
   multi modulo Soluzioni Operative.
2. Access resta il database compatibile oggi, quindi il provider predefinito
   rimane "access".
3. PostgreSQL e il target definitivo, quindi i campi PostgreSQL sono gia
   presenti ma non attivi.
4. Percorsi, porte, URL, codice modulo e feature flags devono smettere di
   vivere sparsi tra backend, Python legacy, estensione Chrome e frontend.
5. Il repository pattern e il service layer potranno dipendere da questa
   configurazione senza conoscere dettagli locali della macchina di sviluppo.

Il modulo usa solo la standard library per ridurre il rischio di regressioni:
non introduce nuove dipendenze e non vincola ancora il progetto a librerie di
settings esterne. Se in futuro si vorra passare a pydantic-settings, questa
classe potra diventare il contratto da preservare.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from functools import lru_cache
import os
from pathlib import Path


def _env_bool(name: str, default: bool) -> bool:
    """Legge un booleano da variabile d'ambiente mantenendo default sicuri.

    I feature flag dello Step 1 devono essere conservativi: se una variabile
    non e definita, il sistema deve restare nel comportamento gia noto. Per
    questo motivo la funzione accetta molte forme testuali comuni, ma non forza
    mai nuove funzionalita quando il valore e assente.
    """

    raw_value = os.getenv(name)

    if raw_value is None:
        return default

    normalized_value = raw_value.strip().lower()

    if normalized_value in {"1", "true", "yes", "y", "on"}:
        return True

    if normalized_value in {"0", "false", "no", "n", "off"}:
        return False

    return default


def _env_list(name: str, default: tuple[str, ...]) -> tuple[str, ...]:
    """Legge una lista separata da virgole da variabile d'ambiente.

    Il caso principale e CORS: oggi le origini ammesse sono due URL locali.
    La configurazione centralizzata deve permettere ambienti futuri senza
    cambiare codice, ma i default devono restare identici allo stato attuale.
    """

    raw_value = os.getenv(name)

    if raw_value is None:
        return default

    values = tuple(
        item.strip()
        for item in raw_value.split(",")
        if item.strip()
    )

    return values or default


@dataclass(frozen=True)
class FeatureFlags:
    """Feature flags iniziali per una modernizzazione graduale.

    In Step 1 i flag sono volutamente conservativi. Non devono attivare nuove
    aree funzionali da soli; servono a rendere espliciti i punti di estensione
    e a preparare rollback rapidi quando verranno introdotti audit, metadati,
    health check dettagliato, repository layer pienamente cablato e modalita
    PostgreSQL.
    """

    enable_audit: bool = field(
        default_factory=lambda: _env_bool("PM_ENABLE_AUDIT", False)
    )
    enable_metadata: bool = field(
        default_factory=lambda: _env_bool("PM_ENABLE_METADATA", False)
    )
    enable_health_details: bool = field(
        default_factory=lambda: _env_bool("PM_ENABLE_HEALTH_DETAILS", False)
    )
    enable_new_repository_layer: bool = field(
        default_factory=lambda: _env_bool("PM_ENABLE_NEW_REPOSITORY_LAYER", False)
    )
    enable_postgres_mode: bool = field(
        default_factory=lambda: _env_bool("PM_ENABLE_POSTGRES_MODE", False)
    )


@dataclass(frozen=True)
class AppConfig:
    """Configurazione applicativa condivisa.

    I default rispecchiano lo stato operativo corrente del progetto. Questo e
    importante perche la configurazione viene introdotta prima del refactor dei
    moduli esistenti: quando i file legacy inizieranno a importarla, dovranno
    trovare gli stessi valori che usano oggi.

    Campi principali:

    - `module_code` identifica ProtocolloMonitor dentro Soluzioni Operative.
    - `database_provider` resta "access" finche PostgreSQL non sara attivo.
    - `access_db_path` mantiene compatibilita con il database Access corrente.
    - `postgres_dsn` e predisposto ma non usato nello Step 1.
    - `file_storage_root` rappresenta lo storage documentale locale attuale.
    - `cors_origins` replica le origini Vue/Vite autorizzate oggi.
    """

    app_name: str = os.getenv("PM_APP_NAME", "ProtocolloMonitor")
    platform_name: str = os.getenv("PM_PLATFORM_NAME", "Soluzioni Operative")
    module_code: str = os.getenv("PM_MODULE_CODE", "PROTOCOLLO_MONITOR")
    environment: str = os.getenv("PM_ENVIRONMENT", "development")

    database_provider: str = os.getenv("PM_DATABASE_PROVIDER", "access")
    access_db_path: str = os.getenv(
        "PM_ACCESS_DB_PATH",
        r"C:\Users\fintu\CloudVVF\Documents\Sviluppo\Grisu\ProtocolloMonitor.accdb",
    )
    postgres_dsn: str = os.getenv("PM_POSTGRES_DSN", "")
    postgres_schema: str = os.getenv("PM_POSTGRES_SCHEMA", "protocollo_monitor")

    file_storage_root: Path = Path(
        os.getenv(
            "PM_FILE_STORAGE_ROOT",
            r"C:\Users\fintu\Documents\GitHub\SoluzioniOperative\ProtocolloMonitor\backend\FileServer",
        )
    )

    fastapi_host: str = os.getenv("PM_FASTAPI_HOST", "127.0.0.1")
    fastapi_port: int = int(os.getenv("PM_FASTAPI_PORT", "8000"))
    flask_legacy_host: str = os.getenv("PM_FLASK_LEGACY_HOST", "127.0.0.1")
    flask_legacy_port: int = int(os.getenv("PM_FLASK_LEGACY_PORT", "5000"))
    frontend_port: int = int(os.getenv("PM_FRONTEND_PORT", "5173"))

    cors_origins: tuple[str, ...] = field(
        default_factory=lambda: _env_list(
            "PM_CORS_ORIGINS",
            (
                "http://localhost:5173",
                "http://127.0.0.1:5173",
            ),
        )
    )

    local_user_id: int = int(os.getenv("PM_LOCAL_USER_ID", "1"))
    local_username: str = os.getenv("PM_LOCAL_USERNAME", "utente_locale")

    feature_flags: FeatureFlags = field(default_factory=FeatureFlags)

    @property
    def fastapi_base_url(self) -> str:
        """URL base FastAPI calcolato dai valori host/porta.

        Oggi diversi componenti usano direttamente `http://127.0.0.1:8000`.
        La property mantiene quel valore come derivazione unica, cosi in futuro
        frontend, estensione o script potranno leggere un solo riferimento.
        """

        return f"http://{self.fastapi_host}:{self.fastapi_port}"

    @property
    def flask_legacy_base_url(self) -> str:
        """URL base del server Flask legacy.

        Flask resta presente durante l'inizio della modernizzazione. Esporre il
        suo URL qui permette allo Step 2 di migrare gradualmente gli endpoint di
        acquisizione verso FastAPI senza perdere la mappa del comportamento
        attuale.
        """

        return f"http://{self.flask_legacy_host}:{self.flask_legacy_port}"

    @property
    def is_access_provider(self) -> bool:
        """Indica se il provider dati attivo e Access."""

        return self.database_provider.strip().lower() == "access"

    @property
    def is_postgres_provider(self) -> bool:
        """Indica se il provider dati attivo e PostgreSQL."""

        return self.database_provider.strip().lower() in {"postgres", "postgresql"}


@lru_cache(maxsize=1)
def get_config() -> AppConfig:
    """Restituisce una singola istanza di configurazione per processo.

    La cache evita che variabili d'ambiente e conversioni vengano rilette in
    punti diversi producendo configurazioni divergenti. Nei test futuri, se
    servira cambiare ambiente a runtime, sara sufficiente svuotare la cache con
    `get_config.cache_clear()`.
    """

    return AppConfig()


settings = get_config()
"""Alias esplicito per i moduli che preferiscono importare un oggetto settings.

L'alias non viene ancora usato dai file esistenti per evitare modifiche di
comportamento nello Step 1, ma offre gia un punto di ingresso chiaro per le
attivita successive.
"""
