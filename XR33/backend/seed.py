from database import Base, engine, SessionLocal
from models import Regione, Comando, Utente, Stazione
from auth import hash_password

Base.metadata.create_all(bind=engine)

db = SessionLocal()

if not db.query(Regione).first():
    sicilia = Regione(nome="Sicilia")
    db.add(sicilia)
    db.commit()
    db.refresh(sicilia)

    palermo = Comando(nome="Palermo", regione_id=sicilia.id)
    db.add(palermo)
    db.commit()
    db.refresh(palermo)

    utenti = [
        Utente(username="francesco", password_hash=hash_password("1234"), ruolo="operatore", comando_id=palermo.id),
        Utente(username="mario", password_hash=hash_password("1234"), ruolo="operatore", comando_id=palermo.id),
        Utente(username="luca", password_hash=hash_password("1234"), ruolo="operatore", comando_id=palermo.id),
    ]
    db.add_all(utenti)

    stazioni = [
        Stazione(nome_stazione="CTXR01", comando_id=palermo.id, tipo_app="XR33", attiva=True),
        Stazione(nome_stazione="PAXR06", comando_id=palermo.id, tipo_app="XR33", attiva=True),
    ]
    db.add_all(stazioni)

    db.commit()
    print("Seed completato.")
else:
    print("Dati già presenti.")

db.close()