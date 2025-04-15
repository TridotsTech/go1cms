<template>
  <LayoutHeader>
    <template #left-header>
      <Breadcrumbs :items="breadcrumbs" />
    </template>
    <template #right-header>
      <div class="flex gap-2 justify-end" v-if="alreadyActions">
        <Button
          variant="subtle"
          theme="gray"
          size="md"
          :label="__('Cancel')"
          @click="form.reload()"
          :disabled="!dirty"
        ></Button>
        <Button
          variant="solid"
          theme="blue"
          size="md"
          :label="__('Save')"
          @click="callUpdateDoc"
          :disabled="!dirty"
        ></Button>
      </div>
    </template>
  </LayoutHeader>
  <div class="p-6 overflow-auto">
    <div v-if="msgError" class="p-4 border border-gray-300 rounded-sm mb-4">
      <div class="text-base text-red-600 font-bold mb-2">
        {{ __('An error has occurred') }}:
      </div>
      <ErrorMessage :message="msgError" />
    </div>
    <div v-if="_form" class="p-4 border border-gray-300 rounded-sm mb-4">
      <div class="mb-5">
        <Fields :sections="sections" :data="_form" />
      </div>
      <div>
        <p class="text-sm text-gray-600 mb-2">{{ __('Field List') }}</p>
        <div class="flex flex-col overflow-y-auto">
          <table class="text-base">
            <tr class="border">
              <th class="border p-2 w-auto">{{ __('No.') }}</th>
              <th class="border p-2 min-w-48">{{ __('Display Name') }}</th>
              <th class="border p-2 min-w-48">{{ __('Field Name') }}</th>
              <th class="border p-2 min-w-48">{{ __('Required Field') }}</th>
              <th class="border p-2 min-w-48">{{ __('Visible') }}</th>
              <th class="border p-2 min-w-32"></th>
            </tr>
            <template v-if="_form.form_fields?.length">
              <Draggable
                :list="_form.form_fields"
                @change="applySort()"
                item-key="idx"
                tag="tbody"
                handle=".handle"
              >
                <template #item="{ element, index }">
                  <tr class="border">
                    <td class="border p-2 text-center">
                      <div class="flex items-center gap-2">
                        <DragVerticalIconV1
                          class="h-8 text-gray-700 cursor-move handle"
                        />
                        <div>{{ element.idx }}</div>
                      </div>
                    </td>
                    <td class="border p-2">
                      {{ element.field_label }}
                    </td>
                    <td class="border p-2">
                      {{ element.field_name }}
                    </td>
                    <td class="border p-2 checkbox-custom">
                      <!-- {{ element.field_mandatory ? __('Yes') : __('No') }} -->
                      <FormControl
                        type="checkbox"
                        label=""
                        :modelValue="element.field_mandatory"
                        :disabled="true"
                      />
                    </td>
                    <td class="border p-2 checkbox-custom">
                      <!-- {{ element.field_hidden ? __('Show') : __('Hide') }} -->
                      <FormControl
                        type="checkbox"
                        label=""
                        :modelValue="element.field_hidden"
                        :disabled="true"
                      />
                    </td>
                    <td>
                      <div class="p-2 flex gap-2">
                        <Button
                          variant="solid"
                          theme="gray"
                          size="sm"
                          :label="__('Edit')"
                          @click="editItem(element, index)"
                        ></Button>
                      </div>
                    </td>
                  </tr>
                </template>
              </Draggable>
            </template>
            <template v-else>
              <tr class="border">
                <td
                  class="p-3 text-center text-base text-gray-600"
                  :colspan="6"
                >
                  {{ __('No data available') }}
                </td>
              </tr>
            </template>
          </table>
        </div>
      </div>
    </div>
    <div v-else class="p-4 border border-gray-300 rounded-sm mb-4">
      <div class="flex justify-center h-screen mt-40 text-gray-700">
        <LoadingIndicator class="h-8 w-8" />
      </div>
    </div>
    <FormModal
      v-model="showModalEdit"
      v-model:section="_form.form_fields"
      :fields="currentItemFields"
      :positionEdit="positionEdit"
    ></FormModal>
  </div>
</template>

<script setup>
import Fields from '@/components/Fields.vue'
import LayoutHeader from '@/components/LayoutHeader.vue'
import FormModal from '@/components/Modals/FormModal.vue'
import DragVerticalIconV1 from '@/components/Icons/DragVerticalIconV1.vue'
import Draggable from 'vuedraggable'
import { Breadcrumbs, call, createResource, ErrorMessage } from 'frappe-ui'
import { ref, computed, watch } from 'vue'
import { createToast, errorMessage, warningMessage, validErrApi } from '@/utils'
import { globalStore } from '@/stores/global'
import { useRouter } from 'vue-router'
const router = useRouter()

const { changeLoadingValue } = globalStore()
const props = defineProps({
  formId: {
    type: String,
    required: true,
  },
})
const msgError = ref()
const _form = ref({})

const sections = computed(() => {
  return [
    {
      section: 'section 1',
      columns: 1,
      class: 'md:grid-cols-2',
      fields: [
        {
          label: 'Form name',
          mandatory: true,
          name: 'form_name',
          type: 'data',
          placeholder: 'Enter name',
        },
        {
          label: 'Form type',
          mandatory: false,
          name: 'form_type',
          type: 'select',
          placeholder: 'Select',
          disabled: true,
          options: [
            { label: 'Form lọc', value: 'Form lọc' },
            { label: 'Form liên hệ', value: 'Form liên hệ' },
            { label: 'Form tuyển dụng', value: 'Form tuyển dụng' },
            {
              label: 'Form đăng nhập tài khoản',
              value: 'Form đăng nhập tài khoản',
            },
            {
              label: 'Form đăng ký tài khoản',
              value: 'Form đăng ký tài khoản',
            },
          ],
        },
        {
          label: 'Label for submit button',
          mandatory: false,
          name: 'btn_text',
          type: 'data',
          placeholder: 'Enter',
        },
      ],
    },
  ]
})

const form = createResource({
  url: 'go1_cms.api.forms.get_form',
  params: {
    name: props.formId,
  },
  auto: true,
  transform: (data) => {
    data?.form_fields.forEach((f) => {
      f.field_hidden = f.field_hidden ? 0 : 1
    })
    _form.value = JSON.parse(JSON.stringify(data))
    return data
  },
})

// handle allow actions
const alreadyActions = ref(false)
const dirty = computed(() => {
  return JSON.stringify(form.data) !== JSON.stringify(_form.value)
})

watch(dirty, (val) => {
  alreadyActions.value = true
})

async function callUpdateDoc() {
  msgError.value = null
  if (JSON.stringify(form.data) == JSON.stringify(_form.value)) {
    warningMessage(__('No changes in document'))
    return
  }

  let formUpdate = { ..._form.value }
  formUpdate?.form_fields.forEach((f) => {
    f.field_hidden = f.field_hidden ? 0 : 1
  })

  if (!formUpdate.form_name) {
    msgError.value = __('Form name') + ' ' + __('cannot be empty')
    errorMessage(
      __('An error has occurred'),
      __('Form name') + ' ' + __('cannot be empty'),
    )
    return
  }

  changeLoadingValue(true, __('Saving...'))
  try {
    const doc = await call('go1_cms.api.forms.update_form', {
      data: {
        ...formUpdate,
      },
    })
    if (doc.name) {
      createToast({
        title: __('Saved'),
        icon: 'check',
        iconClasses: 'text-green-600',
      })
      form.reload()
    }
  } catch (err) {
    validErrApi(err, router)

    if (err.messages && err.messages.length) {
      msgError.value = err.messages.join(', ')
      errorMessage(__('An error has occurred'), err.messages.join(', '))
    } else {
      errorMessage(__('An error has occurred'), err)
    }
  }
  changeLoadingValue(false)
}

// show modal edit
const showModalEdit = ref(false)
const currentItem = ref()
const currentItemFields = ref([])
const positionEdit = ref()

function editItem(el, idx) {
  let fields = [
    {
      field_label: __('No.'),
      field_key: 'idx',
      field_type: 'number',
      disabled: true,
      value: el.idx,
    },
    {
      field_label: __('Display Name'),
      field_key: 'field_label',
      field_type: 'text',
      disabled: false,
      value: el.field_label,
    },
    {
      field_label: __('Text placeholder'),
      field_key: 'field_placeholder',
      field_type: 'textarea',
      disabled: false,
      value: el.field_placeholder,
    },
    {
      field_label: __('Required Field'),
      field_key: 'field_mandatory',
      field_type: 'checkbox',
      labelInput: 'Yes',
      disabled: false,
      value: el.field_mandatory,
    },
    {
      field_label: __('Visible'),
      field_key: 'field_hidden',
      labelInput: 'Show',
      field_type: 'checkbox',
      disabled: false,
      value: el.field_hidden,
    },
  ]

  if (el.field_type == 'file') {
    fields.push({
      field_label: __('Maximum file size (MB)'),
      field_key: 'max_file_size',
      field_type: 'number',
      disabled: false,
      value: el.max_file_size,
    })
  } else if (['checkbox', 'select', 'radio'].includes(el.field_type)) {
    fields.push({
      field_label: __('Options (one per line)'),
      field_key: 'field_options',
      field_type: 'textarea',
      disabled: false,
      value: el.field_options,
    })
  }

  currentItemFields.value = fields
  positionEdit.value = idx
  currentItem.value = el
  showModalEdit.value = true
}

watch(
  () => props.formId,
  (val) => {
    form.update({
      params: { name: val },
    })
    form.reload()
  },
)

// breadcrumbs
const breadcrumbs = computed(() => {
  let items = [{ label: __('Form management'), route: { name: 'Forms' } }]
  items.push({
    label: form.data?.form_name,
    route: {},
  })
  return items
})

function applySort() {
  _form.value.form_fields = _form.value.form_fields.map((el, idx) => ({
    ...el,
    idx: idx + 1,
  }))
}
</script>
<style>
.checkbox-custom input[type='checkbox'] {
  color: gray;
}
</style>
