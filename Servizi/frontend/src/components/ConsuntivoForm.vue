<template>
  <v-card>
    <v-card-title class="text-subtitle-1 font-weight-medium pa-4 pb-2">
      Consuntivo turno
    </v-card-title>
    <v-divider/>
    <v-card-text class="pt-4">
      <div class="text-body-2 text-medium-emphasis mb-4">
        {{ presenza.cognome }} {{ presenza.nome_dip }} —
        {{ presenza.data_servizio }}
        ({{ presenza.orario_inizio }}–{{ presenza.orario_fine }})
      </div>
      <v-row dense>
        <v-col cols="6">
          <v-text-field v-model="form.orario_inizio" label="Inizio effettivo"
                        placeholder="08:00"/>
        </v-col>
        <v-col cols="6">
          <v-text-field v-model="form.orario_fine" label="Fine effettiva"
                        placeholder="20:00"/>
        </v-col>
        <v-col cols="12">
          <v-select v-model="form.stato" :items="statiItems" label="Stato *"/>
        </v-col>
        <v-col cols="12">
          <v-textarea v-model="form.note_consuntivo" label="Note variazioni"
                      rows="2" auto-grow/>
        </v-col>
      </v-row>
    </v-card-text>
    <v-divider/>
    <v-card-actions>
      <v-spacer/>
      <v-btn variant="text" @click="$emit('cancel')">Annulla</v-btn>
      <v-btn color="primary" @click="salva">Salva</v-btn>
    </v-card-actions>
  </v-card>
</template>

<script setup>
import { ref } from 'vue'

const props = defineProps({
  presenza: { type: Object, required: true }
})
const emit = defineEmits(['save', 'cancel'])

const statiItems = ['confermato', 'modificato', 'assente']

const form = ref({
  orario_inizio:   props.presenza.orario_inizio || '',
  orario_fine:     props.presenza.orario_fine   || '',
  stato:           props.presenza.stato === 'programmato' ? 'confermato' : props.presenza.stato,
  note_consuntivo: props.presenza.note_consuntivo || '',
})

function salva() {
  emit('save', { ...form.value })
}
</script>
