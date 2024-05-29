<template>
  <Dialog
    v-model="show"
    :options="{
      size: 'xl',
      actions: [
        {
          label: editMode ? 'Cập nhật' : 'Thêm',
          variant: 'solid',
          onClick: () => updateSection(),
        },
      ],
    }"
  >
    <template #body-title>
      <div class="flex items-center gap-3">
        <h3 class="text-2xl font-semibold leading-6 text-gray-900">
          {{ editMode ? 'Chỉnh sửa' : 'Thêm mới' }} - {{ title }}
        </h3>
      </div>
    </template>
    <template #body-content>
      <div class="grid grid-cols-1 gap-4">
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
import { getTypeField } from '@/utils'

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
  let item = props.fields.reduce((oldVal, currentVal) => {
    oldVal[currentVal.field_key] = currentVal.value
    return oldVal
  }, {})
  if (props.editMode) {
    section.value[props.positionEdit] = {
      ...section.value[props.positionEdit],
      ...item,
    }
  } else {
    section.value.push(item)
  }

  section.value.sort(function (a, b) {
    return a.idx - b.idx
  })
  show.value = false
}
</script>
