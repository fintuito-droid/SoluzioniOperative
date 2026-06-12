// moduli.js — Catalogo dei moduli della piattaforma SoluzioniOperative
// Ogni modulo dichiara come appare nella home e dove porta.
// `migrato`: false finché il modulo non è stato portato dentro il frontend unico
// (la tessera appare ma è disabilitata con l'etichetta "In migrazione").
// L'abilitazione per utente arriva dal backend con la sessione (Fase 2).

export const MODULI = [
  {
    codice: 'servizi',
    nome: 'Servizi',
    descrizione: 'Presenze servizi a pagamento — Campagna AIB',
    icona: 'mdi-fire',
    colore: '#c0392b',
    rotta: '/servizi/presenze',
    migrato: true,
  },
  {
    codice: 'protocollo-monitor',
    nome: 'ProtocolloMonitor',
    descrizione: 'Gestione protocolli, pratiche e documenti',
    icona: 'mdi-file-document-multiple-outline',
    colore: '#2c3e50',
    rotta: '/protocollo-monitor/protocolli',
    migrato: true,
  },
  {
    codice: 'xr33',
    nome: 'XR33',
    descrizione: 'Checklist operative apparati XR33',
    icona: 'mdi-clipboard-check-outline',
    colore: '#1565c0',
    rotta: '/xr33',
    migrato: true,
  },
]
