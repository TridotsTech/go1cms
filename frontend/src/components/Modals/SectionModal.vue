<template>
  <Dialog
    v-model="show"
    :options="{
      size: '3xl',
      actions: [
        {
          label: editMode ? __('Update') : __('Add'),
          variant: 'solid',
          onClick: () => updateSection(),
        },
      ],
    }"
  >
    <template #body-title>
      <div class="flex items-center gap-3">
        <h3 class="text-2xl font-semibold leading-6 text-gray-900">
          {{ editMode ? __('Edit') : __('Add New') }} - {{ __(title) }}
        </h3>
      </div>
    </template>
    <template #body-content>
      <div class="flex flex-col gap-4">
        <template v-for="field in fields">
          <div>
            <Field
              v-if="getTypeField(field.field_type) == 'upload_image'"
              :field="{
                label: field.field_label,
                name: field.field_key,
                type: getTypeField(field.field_type),
                placeholder: field.field_label,
              }"
              :imgPreview="field['value']"
              v-model="field['upload_file_image']"
            ></Field>
            <Field
              v-else
              :field="{
                label: field.field_label,
                name: field.field_key,
                type: getTypeField(field.field_type),
                placeholder: field.field_label,
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
import { getTypeField, toBase64 } from '@/utils'

const props = defineProps({
  fields: {
    type: Array,
    default: [],
  },
  editMode: {
    type: Boolean,
    default: false,
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
    if (f.field_type == 'Attach' && f.upload_file_image) {
      item['upload_file_image_' + f.field_key] = f.upload_file_image
      item[f.field_key] = await toBase64(f.upload_file_image)
    } else {
      item[f.field_key] = f.value
    }
  }

  if (props.editMode) {
    section.value[props.positionEdit] = {
      ...section.value[props.positionEdit],
      ...item,
    }
  } else {
    section.value.push(item)
  }

  // section.value.sort(function (a, b) {
  //   return a.idx - b.idx
  // })
  show.value = false
}
</script>
