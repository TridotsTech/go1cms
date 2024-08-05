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
    <div v-if="JSON.stringify(_webSetup) != '{}'">
      <FieldsComponent
        title="Thiết lập chung"
        v-model="_webSetup.fields_cp"
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
import { createToast, errorMessage, handleUploadFieldImage } from '@/utils'
import { globalStore } from '@/stores/global'

const { changeLoadingValue } = globalStore()

const breadcrumbs = [
  { label: 'Thiết lập website', route: { name: 'Website Setup' } },
]
const _webSetup = ref({})
const msgError = ref()

// get detail
const webSetup = createResource({
  url: 'go1_cms.api.web_setup.get_setup',
  method: 'GET',
  auto: true,
  transform: (data) => {
    data.fields_cp.forEach((f) => {
      f.fields.forEach((el) => {
        if (el.classSize && el.field_key == 'favicon') {
          el.classSize = 'h-16 max-w-16'
        }
      })
    })

    _webSetup.value = JSON.parse(JSON.stringify(data))
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
  return JSON.stringify(webSetup.data) !== JSON.stringify(_webSetup.value)
})

watch(dirty, (val) => {
  alreadyActions.value = true
})

async function callUpdateDoc() {
  changeLoadingValue(true, 'Đang lưu...')
  try {
    let data = JSON.parse(JSON.stringify(_webSetup.value))

    // upload image
    await handleUploadFieldImage(
      data,
      _webSetup,
      'Web Theme',
      _webSetup.value.docname,
    )

    let docUpdate = await call('go1_cms.api.web_setup.update_setup', {
      data: data,
    })

    if (docUpdate.name) {
      webSetup.reload()

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

async function cancelSaveDoc() {
  await webSetup.reload()
}
</script>
