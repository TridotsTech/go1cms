<template>
  <Dialog
    v-model="show"
    :options="{
      size: 'xl',
      actions: [
        {
          label: 'Cập nhật',
          variant: 'solid',
          onClick: () => updateSection(),
        },
      ],
    }"
  >
    <template #body-title>
      <div class="flex items-center gap-3">
        <h3 class="text-2xl font-semibold leading-6 text-gray-900">
          Chỉnh sửa
        </h3>
      </div>
    </template>
    <template #body-content>
      <div class="grid grid-cols-1 gap-4">
        <template v-for="field in fields">
          <div>
            <Field
              :field="{
                label: field.field_label,
                name: field.field_key,
                type: getTypeField(field.field_type),
                placeholder: field.field_label,
                labelInput: field.labelInput,
                disabled: field.disabled,
                rows: 7,
              }"
              v-model="field['value']"
            ></Field>
          </div>
        </template>
      </div>
    </template>
  </Dialog>
</template>

<script setup>
import Field from '@/components/Field.vue'
import { getTypeField } from '@/utils'

const props = defineProps({
  fields: {
    type: Array,
    default: [],
  },
  title: {
    type: String,
    default: '',
  },
  positionEdit: {
    type: Number,
    default: 0,
  },
})

const show = defineModel()
const section = defineModel('section')

async function updateSection() {
  let item = {}
  for (const [idx_f, f] of props.fields.entries()) {
    if (['checkbox'].includes(f.field_type)) {
      item[f.field_key] = f.value ? 1 : 0
    } else {
      item[f.field_key] = f.value
    }
  }

  section.value[props.positionEdit] = {
    ...section.value[props.positionEdit],
    ...item,
  }

  show.value = false
}
</script>
