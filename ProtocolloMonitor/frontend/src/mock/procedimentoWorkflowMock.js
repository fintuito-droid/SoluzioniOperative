export const statiWorkflow = {
  NON_AVVIATA: {
    label: 'Non avviata',
    color: 'grey'
  },
  IN_CORSO: {
    label: 'In corso',
    color: 'blue'
  },
  COMPLETATA: {
    label: 'Completata',
    color: 'green'
  },
  BLOCCATA: {
    label: 'Bloccata',
    color: 'red'
  },
  SCADUTA: {
    label: 'Scaduta',
    color: 'orange'
  },
  SOSPESA: {
    label: 'Sospesa',
    color: 'purple'
  }
}

export const catalogoSottofasiMock = [
  {
    codice: 'VERIFICA_OGGETTO',
    titolo: 'Verifica oggetto',
    descrizione: 'Controllo del testo dell oggetto della nota.',
    icona: 'mdi-text-search',
    colore: 'blue'
  },
  {
    codice: 'TELEFONATA',
    titolo: 'Telefonata',
    descrizione: 'Contatto telefonico con ufficio, Comando o referente.',
    icona: 'mdi-phone',
    colore: 'green'
  },
  {
    codice: 'EMAIL',
    titolo: 'Email',
    descrizione: 'Invio o verifica di una comunicazione tramite posta elettronica.',
    icona: 'mdi-email-outline',
    colore: 'indigo'
  },
  {
    codice: 'DOCUMENTO',
    titolo: 'Documento',
    descrizione: 'Predisposizione o verifica di un documento amministrativo.',
    icona: 'mdi-file-document-outline',
    colore: 'deep-purple'
  },
  {
    codice: 'UFFICIO',
    titolo: 'Ufficio competente',
    descrizione: 'Individuazione dell ufficio responsabile della lavorazione.',
    icona: 'mdi-office-building',
    colore: 'cyan'
  },
  {
    codice: 'PRIORITA',
    titolo: 'Priorita',
    descrizione: 'Attribuzione della priorita operativa o amministrativa.',
    icona: 'mdi-alert-circle-outline',
    colore: 'orange'
  },
  {
    codice: 'FIRMA',
    titolo: 'Firma',
    descrizione: 'Acquisizione o verifica della firma del responsabile.',
    icona: 'mdi-draw-pen',
    colore: 'brown'
  },
  {
    codice: 'CONTROLLO',
    titolo: 'Controllo finale',
    descrizione: 'Verifica conclusiva prima della chiusura della fase.',
    icona: 'mdi-check-decagram',
    colore: 'teal'
  }
]

export const procedimentoFasiMock = [
  {
    id: 1,
    ordine: 1,
    titolo: 'Acquisizione nota',
    descrizione: 'Acquisizione della nota da Vigilia e salvataggio dei dati principali.',
    stato: 'COMPLETATA',
    obbligatoria: true,
    bloccante: true,
    responsabile: 'ProtocolloMonitor',
    dataScadenza: '26/05/2026',
    sottofasi: [
      {
        id: 101,
        ordine: 1,
        titolo: 'Lettura HTML',
        descrizione: 'Acquisizione del contenuto HTML dalla pagina Vigilia.',
        stato: 'COMPLETATA',
        icona: 'mdi-code-tags'
      },
      {
        id: 102,
        ordine: 2,
        titolo: 'Estrazione dati',
        descrizione: 'Estrazione dei dati principali dal documento.',
        stato: 'COMPLETATA',
        icona: 'mdi-database-search'
      }
    ]
  },
  {
    id: 2,
    ordine: 2,
    titolo: 'Classificazione documento',
    descrizione: 'Classificazione della nota acquisita e individuazione della tipologia documentale.',
    stato: 'IN_CORSO',
    obbligatoria: true,
    bloccante: true,
    responsabile: 'Ufficio Gare',
    dataScadenza: '27/05/2026',
    sottofasi: [
      {
        id: 201,
        ordine: 1,
        titolo: 'Verifica oggetto',
        descrizione: 'Controllo del testo dell oggetto della nota.',
        stato: 'COMPLETATA',
        icona: 'mdi-text-search'
      },
      {
        id: 202,
        ordine: 2,
        titolo: 'Telefonata',
        descrizione: 'Contatto telefonico con ufficio o referente interessato.',
        stato: 'IN_CORSO',
        icona: 'mdi-phone'
      },
      {
        id: 203,
        ordine: 3,
        titolo: 'Ufficio',
        descrizione: 'Verifica dell ufficio competente alla lavorazione.',
        stato: 'NON_AVVIATA',
        icona: 'mdi-office-building'
      }
    ]
  },
  {
    id: 3,
    ordine: 3,
    titolo: 'Istruttoria',
    descrizione: 'Verifica amministrativa e tecnica della richiesta ricevuta.',
    stato: 'NON_AVVIATA',
    obbligatoria: true,
    bloccante: true,
    responsabile: 'Funzionario istruttore',
    dataScadenza: '03/06/2026',
    sottofasi: []
  }
]
