from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Text, Boolean
from sqlalchemy.sql import func
from database import Base

class Regione(Base):
    __tablename__ = "regioni"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(100), unique=True, nullable=False)

class Comando(Base):
    __tablename__ = "comandi"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(150), nullable=False)
    regione_id = Column(Integer, ForeignKey("regioni.id"), nullable=False)

class Utente(Base):
    __tablename__ = "utenti"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(100), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    ruolo = Column(String(50), nullable=False, default="operatore")
    comando_id = Column(Integer, ForeignKey("comandi.id"), nullable=True)
    attivo = Column(Boolean, default=True)

class Stazione(Base):
    __tablename__ = "stazioni"

    id = Column(Integer, primary_key=True, index=True)
    nome_stazione = Column(String(100), nullable=False)
    comando_id = Column(Integer, ForeignKey("comandi.id"), nullable=False)
    tipo_app = Column(String(50), nullable=False, default="XR33")
    attiva = Column(Boolean, default=True)

class Checklist(Base):
    __tablename__ = "checklist"

    id = Column(Integer, primary_key=True, index=True)
    app = Column(String(50), nullable=False, default="XR33")
    stazione_id = Column(Integer, ForeignKey("stazioni.id"), nullable=False)
    comando_id = Column(Integer, ForeignKey("comandi.id"), nullable=False)
    utente_creatore_id = Column(Integer, ForeignKey("utenti.id"), nullable=False)
    tipo_attivita = Column(String(30), nullable=False)
    note_generali = Column(Text, nullable=True)
    data_intervento = Column(DateTime(timezone=True), server_default=func.now())

class ChecklistOperatore(Base):
    __tablename__ = "checklist_operatori"

    id = Column(Integer, primary_key=True, index=True)
    checklist_id = Column(Integer, ForeignKey("checklist.id", ondelete="CASCADE"), nullable=False)
    utente_id = Column(Integer, ForeignKey("utenti.id"), nullable=False)

class ChecklistDettaglio(Base):
    __tablename__ = "checklist_dettagli"

    id = Column(Integer, primary_key=True, index=True)
    checklist_id = Column(Integer, ForeignKey("checklist.id", ondelete="CASCADE"), nullable=False)
    tipo_controllo = Column(String(100), nullable=False)
    esito = Column(String(20), nullable=True)
    note = Column(Text, nullable=True)
    foto_path = Column(Text, nullable=True)