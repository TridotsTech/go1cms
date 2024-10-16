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
          label="Hủy"
          :disabled="!dirty"
          @click="cancelSaveDoc"
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
    <div v-if="JSON.stringify(_settings) != '{}'">
      <FieldsComponent
        title="Cài đặt chung"
        v-model="_settings.fields_cp"
      ></FieldsComponent>
    </div>
    <div v-else class="p-4 border border-gray-300 rounded-sm mb-4">
      <div class="flex justify-center h-screen mt-40 text-gray-700">
        <LoadingIndicator class="h-8 w-8" />
      </div>
    </div>
  </div>
</template>

<script setup>
import LayoutHeader from '@/components/LayoutHeader.vue'
import FieldsComponent from '@/components/FieldsPage/FieldsComponent.vue'
import { Breadcrumbs, ErrorMessage, createResource, call } from 'frappe-ui'
import { ref, computed, watch } from 'vue'
import { createToast, errorMessage, validErrApi } from '@/utils'
import { globalStore } from '@/stores/global'
import { useRouter } from 'vue-router'
const router = useRouter()

const { changeLoadingValue } = globalStore()

const breadcrumbs = [{ label: 'Cài đặt', route: { name: 'CMS Settings' } }]
const _settings = ref({})
const msgError = ref()

// get detail
const settings = createResource({
  url: 'go1_cms.api.settings.get_setup',
  method: 'GET',
  auto: true,
  transform: (data) => {
    _settings.value = JSON.parse(JSON.stringify(data))
    return data
  },
  onError: (err) => {
    validErrApi(err, router)
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
  if (_settings.value?.fields_cp) {
    let show_edit = false
    if (_settings.value?.fields_cp[0].fields[0].content) {
      show_edit = true
    }
    _settings.value.fields_cp[0].fields[1].show_edit = show_edit

    show_edit = false
    if (_settings.value?.fields_cp[1].fields[2].content) {
      show_edit = true
    }
    _settings.value.fields_cp[1].fields[3].show_edit = show_edit
  }
  return JSON.stringify(settings.data) !== JSON.stringify(_settings.value)
})

watch(dirty, (val) => {
  alreadyActions.value = true
})

async function callUpdateDoc() {
  changeLoadingValue(true, 'Đang lưu...')
  try {
    let data = JSON.parse(JSON.stringify(_settings.value))

    let docUpdate = await call('go1_cms.api.settings.update_setup', {
      data: data,
    })

    if (docUpdate.name) {
      settings.reload()

      createToast({
        title: 'Cập nhật thành công',
        icon: 'check',
        iconClasses: 'text-green-600',
      })
    }
  } catch (err) {
    validErrApi(err, router)
    if (err.messages && err.messages.length) {
      msgError.value = err.messages.join(', ')
      errorMessage('Có lỗi xảy ra', err.messages.join(', '))
    } else {
      errorMessage('Có lỗi xảy ra', err)
    }
  }
  changeLoadingValue(false)
}

async function cancelSaveDoc() {
  await settings.reload()
}
</script>
