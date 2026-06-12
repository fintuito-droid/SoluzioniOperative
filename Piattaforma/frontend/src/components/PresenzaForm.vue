<template>
  <v-card>
    <v-card-title class="text-subtitle-1 font-weight-medium pa-4 pb-2">
      Nuovo turno programmato
    </v-card-title>
    <v-divider/>
    <v-card-text class="pt-4">
      <v-row dense>
        <v-col cols="12" sm="6">
          <v-select
            v-model="form.personale_id"
            :items="personaleList"
            :item-title="p => `${p.cognome} ${p.nome}`"
            item-value="id"
            label="Dipendente *"
            :rules="[v => !!v || 'Campo obbligatorio']"
          />
        </v-col>
        <v-col cols="12" sm="6">
          <v-select
            v-model="form.funzione_id"
            :items="funzioni"
            item-title="codice"
            item-value="id"
            label="Funzione *"
            :rules="[v => !!v || 'Campo obbligatorio']"
          />
        </v-col>
        <v-col cols="12" sm="6">
          <v-select
            v-model="form.postazione_id"
            :items="postazioni"
            item-title="codice"
            item-value="id"
            label="Postazione *"
            :rules="[v => !!v || 'Campo obbligatorio']"
          />
        </v-col>
        <v-col cols="12" sm="6">
          <v-text-field
            v-model="form.data_servizio"
            type="date"
            label="Data servizio *"
            :rules="[v => !!v || 'Campo obbligatorio']"
          />
        </v-col>
        <v-col cols="6" sm="3">
          <v-text-field v-model="form.orario_inizio" label="Inizio *" placeholder="08:00"
                        :rules="[v => /^\d{2}:\d{2}$/.test(v) || 'HH:MM']"/>
        </v-col>
        <v-col cols="6" sm="3">
          <v-text-field v-model="form.orario_fine" label="Fine *" placeholder="20:00"
                        :rules="[v => /^\d{2}:\d{2}$/.test(v) || 'HH:MM']"/>
        </v-col>
        <v-col cols="12">
          <v-textarea v-model="form.note_consuntivo" label="Note" rows="2" auto-grow/>
        </v-col>
      </v-row>
    </v-card-text>
    <v-divider/>
    <v-card-actions>
      <v-spacer/>
      <v-btn variant="text" @click="$emit('cancel')">Annulla</v-btn>
      <v-btn color="primary" :disabled="!isValid" @click="salva">Salva</v-btn>
    </v-card-actions>
  </v-card>
</template>

<script setup>
import { ref, computed } from 'vue'

const props = defineProps({
  campagnaId:       { type: Number, default: null },
  personaleList:    { type: Array,  default: () => [] },
  postazioni:       { type: Array,  default: () => [] },
  funzioni:         { type: Array,  default: () => [] },
  dataPrecompilata: { type: String, default: '' },
})
const emit = defineEmits(['save', 'cancel'])

const form = ref({
  personale_id:    null,
  funzione_id:     null,
  postazione_id:   null,
  data_servizio:   props.dataPrecompilata,
  orario_inizio:   '08:00',
  orario_fine:     '20:00',
  note_consuntivo: '',
})

const isValid = computed(() =>
  form.value.personale_id &&
  form.value.funzione_id &&
  form.value.postazione_id &&
  form.value.data_servizio &&
  /^\d{2}:\d{2}$/.test(form.value.orario_inizio) &&
  /^\d{2}:\d{2}$/.test(form.value.orario_fine)
)

function salva() {
  emit('save', { ...form.value, campagna_id: props.campagnaId })
}
</script>
