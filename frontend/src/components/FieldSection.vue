<template>
  <template v-if="field.allow_edit">
    <div
      class="col-span-2 flex flex-col overflow-y-auto"
      v-if="field.field_type == 'List'"
    >
      <table class="text-base">
        <tr class="border">
          <th class="border p-2 w-auto">STT</th>
          <template v-for="f in field.fields_json">
            <th class="border p-2 min-w-48">{{ f.field_label }}</th>
          </template>
          <th class="border p-2 min-w-32"></th>
        </tr>
        <template v-if="field.content.length">
          <Draggable
            :list="field.content"
            @end="applySort(field)"
            item-key="idx"
            tag="tbody"
          >
            <template #item="{ element, index }">
              <tr class="border">
                <td class="border p-2 text-center">
                  <div class="flex items-center gap-2">
                    <DragVerticalIconV1 class="h-8 text-gray-700 cursor-move" />
                    <div>{{ element.idx }}</div>
                  </div>
                </td>
                <template v-for="fj in field.fields_json">
                  <td class="border p-2">
                    {{ element[fj.field_key] }}
                  </td>
                </template>
                <td class="p-2 flex gap-2">
                  <Button
                    variant="solid"
                    theme="gray"
                    size="sm"
                    label="Sửa"
                    @click="editItemSection(field, index)"
                  ></Button>
                  <Button
                    variant="solid"
                    theme="red"
                    size="sm"
                    label="Xóa"
                    @click="deleteItemSection(field, index)"
                  ></Button>
                </td>
              </tr>
            </template>
          </Draggable>
        </template>
        <template v-else>
          <tr class="border">
            <td
              class="p-3 text-center text-base text-gray-600"
              :colspan="field.fields_json.length + 2"
            >
              Không có dữ liệu
            </td>
          </tr>
        </template>
      </table>
      <div class="flex py-2">
        <Button
          variant="solid"
          theme="blue"
          size="sm"
          label="Thêm"
          @click="createItemSection(field)"
        ></Button>
      </div>
    </div>
    <div class="flex flex-col" v-else>
      <Field
        v-if="getTypeField(field.field_type) == 'upload_image'"
        :field="{
          label: field.field_label,
          name: field.field_key,
          type: getTypeField(field.field_type),
          placeholder: field.field_label,
          rows: 7,
        }"
        :imgPreview="field['content']"
        v-model="field['upload_file_image']"
      ></Field>
      <Field
        v-else
        :field="{
          label: field.field_label,
          name: field.field_key,
          type: getTypeField(field.field_type),
          placeholder: field.field_label,
          rows: 7,
          doctype: field.doctype,
          filters: field.filters,
        }"
        v-model="field['content']"
      ></Field>
    </div>
  </template>
  <SectionModal
    :fields="currentItemFields"
    v-model="showSectionModal"
    v-model:section="currentItemSection"
    :editMode="editMode"
    :title="sectionName"
    :positionEdit="positionEdit"
  />
</template>

<script setup>
import Field from '@/components/Field.vue'
import DragVerticalIconV1 from '@/components/Icons/DragVerticalIconV1.vue'
import Draggable from 'vuedraggable'
import SectionModal from '@/components/Modals/SectionModal.vue'
import { getTypeField } from '@/utils'
import { ref, watch } from 'vue'

const props = defineProps({
  field: {
    type: Object,
    default: {},
  },
  sectionName: {
    type: String,
    default: '',
  },
})

const showSectionModal = ref(false)
const currentItemSection = ref()
const currentItemFields = ref([])
const editMode = ref(false)
const positionEdit = ref()

function createItemSection(field) {
  let fields = field.fields_json.map((fj) => ({
    field_label: fj.field_label,
    field_key: fj.field_key,
    field_type: fj.field_type,
    value: null,
    upload_file_image: null,
  }))

  fields.unshift({
    field_label: 'STT',
    field_key: 'idx',
    field_type: 'number',
    disabled: true,
    value: field.content.length + 1,
  })

  editMode.value = false
  currentItemFields.value = fields
  currentItemSection.value = field.content
  showSectionModal.value = true
}

function editItemSection(field, idx) {
  let item = field.content[idx]
  let fields = field.fields_json.map((fj) => ({
    field_label: fj.field_label,
    field_key: fj.field_key,
    field_type: fj.field_type,
    value: item[fj.field_key],
    upload_file_image: null,
  }))
  fields.unshift({
    field_label: 'STT',
    field_key: 'idx',
    field_type: 'number',
    disabled: true,
    value: item.idx,
  })

  positionEdit.value = idx
  editMode.value = true
  currentItemFields.value = fields
  currentItemSection.value = field.content
  showSectionModal.value = true
}

function deleteItemSection(field, idx) {
  field.content.splice(idx, 1)
  applySort(field)
}

function applySort(field) {
  field['content'] = field.content.map((el, idx) => ({ ...el, idx: idx + 1 }))
}
</script>
