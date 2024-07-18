<template>
  <LayoutHeader>
    <template #left-header>
      <Breadcrumbs :items="breadcrumbs" />
    </template>
  </LayoutHeader>
  <div class="p-6 overflow-auto">
    <div v-if="msgError" class="p-4 border border-gray-300 rounded-sm mb-4">
      <div class="text-base text-red-600 font-bold mb-2">Có lỗi xảy ra:</div>
      <ErrorMessage :message="msgError" />
    </div>
    <div class="p-4 border border-gray-300 rounded-sm mb-4">
      <h2 class="font-bold text-lg mb-4">Hành động</h2>
      <div class="flex gap-6">
        <Button
          :variant="'solid'"
          theme="gray"
          size="sm"
          label="Tạo File"
          :loading="false"
          @click="callCreateFile"
        >
        </Button>
        <Button
          :variant="'solid'"
          theme="gray"
          size="sm"
          label="Cập nhật mẫu từ File"
          :loading="false"
          @click="callUpdateTemplate"
        >
        </Button>
      </div>
    </div>
  </div>
</template>

<script setup>
import LayoutHeader from '@/components/LayoutHeader.vue'
import { Breadcrumbs, ErrorMessage, call } from 'frappe-ui'
import { ref } from 'vue'
import { createToast, errorMessage } from '@/utils'
import { globalStore } from '@/stores/global'

const { changeLoadingValue } = globalStore()

const breadcrumbs = [
  { label: 'Trình tạo', route: { name: 'Setup File Template' } },
]

const msgError = ref()

async function callCreateFile() {
  changeLoadingValue(true, 'Đang tạo file...')
  try {
    let docUpdate = await call(
      'go1_cms.api.setup_file_template.create_file_json',
      {},
    )

    if (docUpdate.msg) {
      createToast({
        title: 'Tạo thành công',
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

async function callUpdateTemplate() {
  changeLoadingValue(true, 'Đang cập nhật...')
  try {
    let docUpdate = await call(
      'go1_cms.api.setup_file_template.update_from_json',
      {},
    )

    if (docUpdate.msg) {
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
</script>
