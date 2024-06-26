<template>
  <LayoutHeader>
    <template #left-header>
      <Breadcrumbs :items="breadcrumbs" />
    </template>
    <template #right-header>
      <div
        class="gap-2 justify-end"
        :class="alreadyActions ? 'flex' : 'hidden'"
      >
        <Button
          variant="subtle"
          theme="gray"
          size="md"
          label="Hủy"
          :disabled="!dirty"
          @click="cacelSaveDoc"
        ></Button>
        <Button
          :variant="'solid'"
          theme="blue"
          size="md"
          label="Lưu"
          :disabled="!dirty"
          @click="callUpdateDoc"
        >
        </Button>
      </div>
    </template>
  </LayoutHeader>
  <div class="p-6 overflow-auto">
    <div v-if="msgError" class="p-4 border border-gray-300 rounded-sm mb-4">
      <div class="text-base text-red-600 font-bold mb-2">Có lỗi xảy ra:</div>
      <ErrorMessage :message="msgError" />
    </div>
    <FieldsComponent
      title="Cấu hình biểu mẫu liên hệ"
      v-model="_email_setup.fields_cp"
    ></FieldsComponent>
  </div>
</template>

<script setup>
import LayoutHeader from '@/components/LayoutHeader.vue'
import FieldsComponent from '@/components/FieldsPage/FieldsComponent.vue'
import { Breadcrumbs, ErrorMessage, createResource, call } from 'frappe-ui'
import { ref, computed, watch } from 'vue'
import { createToast, errorMessage } from '@/utils'
import { globalStore } from '@/stores/global'

const { changeLoadingValue } = globalStore()

const breadcrumbs = [
  { label: 'Cấu hình biểu mẫu', route: { name: 'Form Setup' } },
]
const _email_setup = ref({})
const msgError = ref()

// get detail
const form_setup = createResource({
  url: 'go1_cms.api.form_setup.get_setup',
  method: 'GET',
  auto: true,
  transform: (data) => {
    _email_setup.value = JSON.parse(JSON.stringify(data))
    return data
  },
  onError: (err) => {
    if (err.messages && err.messages.length) {
      msgError.value = err.messages.join(', ')
      errorMessage('Có lỗi xảy ra', err.messages.join(', '))
    } else {
      errorMessage('Có lỗi xảy ra', err)
    }
  },
})

// handle allow actions
const alreadyActions = ref(false)
const dirty = computed(() => {
  if (_email_setup.value?.fields_cp) {
    let show_edit = false
    if (_email_setup.value?.fields_cp[0].fields[0].content) {
      show_edit = true
    }
    _email_setup.value.fields_cp[0].fields[1].show_edit = show_edit
  }
  return JSON.stringify(form_setup.data) !== JSON.stringify(_email_setup.value)
})

watch(dirty, (val) => {
  alreadyActions.value = true
})

async function callUpdateDoc() {
  changeLoadingValue(true, 'Đang lưu...')
  try {
    let data = JSON.parse(JSON.stringify(_email_setup.value))

    let docUpdate = await call('go1_cms.api.form_setup.update_setup', {
      data: data,
    })

    if (docUpdate.name) {
      form_setup.reload()

      createToast({
        title: 'Cập nhật thành công',
        icon: 'check',
        iconClasses: 'text-green-600',
      })
    }
  } catch (err) {
    if (err.messages && err.messages.length) {
      msgError.value = err.messages.join(', ')
      errorMessage('Có lỗi xảy ra', err.messages.join(', '))
    } else {
      errorMessage('Có lỗi xảy ra', err)
    }
  }
  changeLoadingValue(false)
}

async function cacelSaveDoc() {
  await form_setup.reload()
}
</script>
