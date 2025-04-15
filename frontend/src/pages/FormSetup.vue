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
          :disabled="!dirty"
          @click="cancelSaveDoc"
        ></Button>
        <Button
          :variant="'solid'"
          theme="blue"
          size="md"
          :label="__('Save')"
          :disabled="!dirty"
          @click="callUpdateDoc"
        >
        </Button>
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
    <div v-if="JSON.stringify(_email_setup) != '{}'">
      <FieldsComponent
        title="Cấu hình biểu mẫu liên hệ"
        v-model="_email_setup.fields_cp"
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
    validErrApi(err, router)
    if (err.messages && err.messages.length) {
      msgError.value = err.messages.join(', ')
      errorMessage(__('An error has occurred'), err.messages.join(', '))
    } else {
      errorMessage(__('An error has occurred'), err)
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
  changeLoadingValue(true, __('Saving...'))
  try {
    let data = JSON.parse(JSON.stringify(_email_setup.value))

    let docUpdate = await call('go1_cms.api.form_setup.update_setup', {
      data: data,
    })

    if (docUpdate.name) {
      form_setup.reload()

      createToast({
        title: __('Saved'),
        icon: 'check',
        iconClasses: 'text-green-600',
      })
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

async function cancelSaveDoc() {
  await form_setup.reload()
}
</script>
