<template>
  <v-container fluid>
    <v-row justify="center">
      <v-col cols="12" xl="11">
        <v-card rounded="xl" elevation="3">
          <v-card-title class="text-h5 py-4">
            Checklist XR33
          </v-card-title>

          <v-divider />

          <v-card-text class="pt-6">
            <v-form @submit.prevent="salvaChecklist">
              <v-row>
                <v-col cols="12" md="6" lg="4">
                  <v-select
                    v-model="form.stazione"
                    :items="stazioni"
                    item-title="label"
                    item-value="value"
                    label="Stazione"
                    variant="outlined"
                    prepend-inner-icon="mdi-radio-tower"
                    :rules="[rules.required]"
                    :loading="loadingStazioni"
                    :disabled="salvataggioInCorso"
                  />
                </v-col>

                <v-col cols="12" md="6" lg="4">
                  <v-select
                    v-model="form.tipoAttivita"
                    :items="tipiAttivita"
                    label="Tipo attività"
                    variant="outlined"
                    prepend-inner-icon="mdi-clipboard-check-outline"
                    :rules="[rules.required]"
                    :disabled="salvataggioInCorso"
                  />
                </v-col>

                <v-col cols="12" lg="4">
                  <v-select
                    v-model="form.operatori"
                    :items="operatoriDisponibili"
                    item-title="title"
                    item-value="value"
                    label="Operatori"
                    variant="outlined"
                    prepend-inner-icon="mdi-account-group"
                    multiple
                    chips
                    closable-chips
                    hint="Seleziona massimo 3 operatori. Includi anche l'utente loggato."
                    persistent-hint
                    :rules="[rules.required, rules.maxOperatori]"
                    :loading="loadingOperatori"
                    :disabled="salvataggioInCorso"
                  />
                </v-col>
              </v-row>

              <v-card class="mt-6" rounded="lg" variant="tonal">
                <v-card-title class="text-subtitle-1">
                  Controlli tecnici
                </v-card-title>

                <v-card-text>
                  <v-row>
                    <v-col
                      v-for="controllo in controlliConfig"
                      :key="controllo.key"
                      cols="12"
                      md="6"
                      lg="4"
                    >
                      <v-card variant="outlined" class="pa-3 h-100">
                        <div class="text-subtitle-2 mb-2">
                          {{ controllo.label }}
                        </div>

                        <v-switch
                          v-model="form.controlli[controllo.key].ok"
                          color="success"
                          inset
                          label="Esito OK"
                          :disabled="salvataggioInCorso"
                        />

                        <v-textarea
                          v-model="form.controlli[controllo.key].note"
                          :label="`Note - ${controllo.label}`"
                          variant="outlined"
                          rows="2"
                          auto-grow
                          class="mt-2"
                          :disabled="salvataggioInCorso"
                        />

                        <v-file-input
                          v-model="form.controlli[controllo.key].foto"
                          :label="`Foto - ${controllo.label}`"
                          variant="outlined"
                          accept="image/*"
                          prepend-inner-icon="mdi-camera"
                          prepend-icon=""
                          class="mt-2"
                          :disabled="salvataggioInCorso"
                          show-size
                          chips
                        />
                      </v-card>
                    </v-col>
                  </v-row>
                </v-card-text>
              </v-card>

              <v-row class="mt-4">
                <v-col cols="12">
                  <v-textarea
                    v-model="form.note"
                    label="Note generali"
                    variant="outlined"
                    rows="4"
                    auto-grow
                    prepend-inner-icon="mdi-text-box-outline"
                    :disabled="salvataggioInCorso"
                  />
                </v-col>
              </v-row>

              <v-alert
                v-if="errore"
                type="error"
                variant="tonal"
                class="mt-4"
              >
                {{ errore }}
              </v-alert>

              <div class="d-flex justify-end mt-6">
                <v-btn
                  color="primary"
                  size="large"
                  type="submit"
                  :loading="salvataggioInCorso"
                >
                  Salva checklist
                </v-btn>
              </div>
            </v-form>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>

    <v-snackbar
      v-model="snackbar"
      color="success"
      timeout="3000"
    >
      Checklist salvata correttamente
    </v-snackbar>
  </v-container>
</template>

<script setup>
import { reactive, ref, onMounted } from "vue";

const API_BASE = "http://127.0.0.1:8000";

const stazioni = ref([]);
const operatoriDisponibili = ref([]);

const loadingStazioni = ref(false);
const loadingOperatori = ref(false);
const salvataggioInCorso = ref(false);
const snackbar = ref(false);
const errore = ref("");

const tipiAttivita = ["Sopralluogo", "Manutenzione"];

const controlliConfig = [
  { key: "alimentazione_rete", label: "Presenza tensione rete" },
  { key: "alimentatore", label: "Stato alimentatore" },
  { key: "ups", label: "Stato gruppo continuità / UPS" },
  { key: "cavi_alimentazione", label: "Integrità cavi alimentazione" },
  { key: "protezioni", label: "Verifica differenziale / protezioni" },
  { key: "modem", label: "Modem" },
  { key: "segnale_modem", label: "Qualità segnale modem" },
  { key: "trasmissione_dati", label: "Trasmissione dati verso centrale" },
  { key: "linea_dati", label: "Stato linea telefonica / dati" },
  { key: "apparato_radio", label: "Stato antenna / apparati radio" },
  { key: "collegamento_radio_vvf", label: "Verifica collegamento radio VVF" },
  { key: "unita_xr33", label: "Unità XR33 accesa" },
  { key: "display_segnalazioni", label: "Display / segnalazioni regolari" },
  { key: "allarmi_locali", label: "Assenza allarmi locali" },
  { key: "contenitore", label: "Integrità contenitore / armadio" },
  { key: "ventole", label: "Stato ventole / aerazione" },
  { key: "pulizia_apparati", label: "Pulizia apparati" },
  { key: "sensore_principale", label: "Sensore principale collegato" },
  { key: "sensore_acquisizione", label: "Sensore in acquisizione" },
  { key: "cablaggi_sensori", label: "Cablaggi sensori integri" },
  { key: "errori_misura", label: "Assenza errori di misura" },
  { key: "coerenza_dati", label: "Coerenza dati trasmessi" },
  { key: "accessibilita_sito", label: "Accessibilità del sito" },
  { key: "stato_locale", label: "Stato locale / box" },
  { key: "infiltrazioni", label: "Assenza infiltrazioni" },
  { key: "manomissioni", label: "Assenza manomissioni" },
  { key: "serrature", label: "Integrità serrature" },
  { key: "etichette_documentazione", label: "Presenza documentazione / etichette" },
  { key: "stazione_operativa", label: "Stazione operativa" },
  { key: "necessita_manutenzione", label: "Necessita manutenzione" },
  { key: "intervento_risolutivo", label: "Intervento risolutivo eseguito" },
  { key: "richiesta_intervento", label: "Richiesta ulteriore intervento" },
];

function creaControlliIniziali() {
  const obj = {};
  for (const c of controlliConfig) {
    obj[c.key] = {
      ok: false,
      note: "",
      foto: null,
    };
  }
  return obj;
}

const form = reactive({
  stazione: null,
  tipoAttivita: null,
  operatori: [],
  controlli: creaControlliIniziali(),
  note: "",
});

const rules = {
  required: (v) =>
    (Array.isArray(v) ? v.length > 0 : !!v) || "Campo obbligatorio",
  maxOperatori: (v) =>
    (!Array.isArray(v) || v.length <= 3) || "Puoi selezionare massimo 3 operatori",
};

function resetForm() {
  form.stazione = null;
  form.tipoAttivita = null;
  form.operatori = [];
  form.note = "";

  for (const controllo of controlliConfig) {
    form.controlli[controllo.key].ok = false;
    form.controlli[controllo.key].note = "";
    form.controlli[controllo.key].foto = null;
  }
}

function normalizzaSingoloFile(fileValue) {
  if (!fileValue) return null;
  if (Array.isArray(fileValue)) return fileValue[0] ?? null;
  return fileValue;
}

async function caricaStazioni() {
  loadingStazioni.value = true;
  try {
    const token = localStorage.getItem("token");
    const response = await fetch(`${API_BASE}/stazioni`, {
      headers: { Authorization: `Bearer ${token}` },
    });
    if (!response.ok) {
      const testoErrore = await response.text();
      throw new Error(`Errore caricamento stazioni: ${testoErrore}`);
    }
    const data = await response.json();
    stazioni.value = data.map((s) => ({
      label: s.nome_stazione ?? s.nome ?? s.codice ?? `Stazione ${s.id}`,
      value: s.id,
    }));
  } catch (err) {
    console.error(err);
    errore.value = err.message || "Errore nel caricamento delle stazioni.";
  } finally {
    loadingStazioni.value = false;
  }
}

async function caricaOperatori() {
  loadingOperatori.value = true;
  try {
    const token = localStorage.getItem("token");
    const response = await fetch(`${API_BASE}/operatori`, {
      headers: { Authorization: `Bearer ${token}` },
    });
    if (!response.ok) {
      const testoErrore = await response.text();
      throw new Error(`Errore caricamento operatori: ${testoErrore}`);
    }
    const data = await response.json();
    operatoriDisponibili.value = data.map((o) => ({
      title: o.username ?? o.nome_completo ?? ([o.nome, o.cognome].filter(Boolean).join(" ") || `Utente ${o.id}`),
      value: o.id,
    }));
  } catch (err) {
    console.error(err);
    errore.value = err.message || "Errore nel caricamento degli operatori.";
  } finally {
    loadingOperatori.value = false;
  }
}

async function uploadFotoControllo(stazioneId, tipoControllo, fileValue) {
  const file = normalizzaSingoloFile(fileValue);
  if (!file) return null;

  const token = localStorage.getItem("token");
  const formData = new FormData();
  formData.append("stazione_id", stazioneId);
  formData.append("tipo_controllo", tipoControllo);
  formData.append("foto", file);

  const response = await fetch(`${API_BASE}/upload-foto`, {
    method: "POST",
    headers: {
      Authorization: `Bearer ${token}`,
    },
    body: formData,
  });

  if (!response.ok) {
    const testoErrore = await response.text();
    throw new Error(`Errore upload ${tipoControllo}: ${testoErrore}`);
  }

  const data = await response.json();
  return data.foto_path;
}

async function salvaChecklist() {
  errore.value = "";

  if (!form.stazione || !form.tipoAttivita || form.operatori.length === 0) {
    errore.value = "Compila i campi obbligatori.";
    return;
  }

  if (form.operatori.length > 3) {
    errore.value = "Puoi selezionare massimo 3 operatori.";
    return;
  }

  salvataggioInCorso.value = true;

  try {
    const token = localStorage.getItem("token");
    const controlliPayload = [];

    for (const controllo of controlliConfig) {
      const fotoPath = await uploadFotoControllo(
        form.stazione,
        controllo.key,
        form.controlli[controllo.key].foto
      );

      controlliPayload.push({
        tipo_controllo: controllo.key,
        esito: form.controlli[controllo.key].ok ? "OK" : "KO",
        note: form.controlli[controllo.key].note || null,
        foto_path: fotoPath,
      });
    }

    const payload = {
      stazione_id: form.stazione,
      tipo_attivita: form.tipoAttivita,
      note_generali: form.note || null,
      operatori_ids: form.operatori,
      controlli: controlliPayload,
    };

    const response = await fetch(`${API_BASE}/checklist`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify(payload),
    });

    if (!response.ok) {
      const testoErrore = await response.text();
      throw new Error(`Errore backend: ${testoErrore}`);
    }

    snackbar.value = true;
    resetForm();
  } catch (err) {
    console.error(err);
    errore.value = err.message || "Errore generico.";
  } finally {
    salvataggioInCorso.value = false;
  }
}

onMounted(async () => {
  await Promise.all([caricaStazioni(), caricaOperatori()]);
});
</script>