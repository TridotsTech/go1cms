<template>
  <LayoutHeader>
    <template #left-header>
      <Breadcrumbs :items="breadcrumbs" />
    </template>
    <template #right-header>
      <div class="flex gap-2 justify-end" v-if="alreadyActions">
        <Tooltip text="Xem trang" :hover-delay="1" :placement="'top'">
          <div>
            <Button
              variant="subtle"
              theme="blue"
              size="md"
              label=""
              icon="eye"
              :link="
                views.data?.config_domain?.use_other_domain
                  ? views.data?.config_domain?.domain + _footer?.web_page?.route
                  : _footer?.web_page?.route
              "
            >
            </Button>
          </div>
        </Tooltip>
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
    <div v-if="JSON.stringify(_footer) != '{}'">
      <FieldsComponent v-model="_footer.fields_cp"></FieldsComponent>
      <FieldsSectionComponent
        v-model="_footer.fields_st_cp"
      ></FieldsSectionComponent>
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
import FieldsSectionComponent from '@/components/FieldsPage/FieldsSectionComponent.vue'
import { Breadcrumbs, ErrorMessage, createResource, call } from 'frappe-ui'
import { ref, computed, watch } from 'vue'
import {
  createToast,
  errorMessage,
  handleUploadFieldImage,
  validErrApi,
} from '@/utils'
import { globalStore } from '@/stores/global'
const { changeLoadingValue } = globalStore()
import { useRouter } from 'vue-router'
const router = useRouter()
import { viewsStore } from '@/stores/views'
const { views } = viewsStore()

const breadcrumbs = [{ label: 'Chân trang', route: { name: 'Footer Page' } }]
const _footer = ref({})
const msgError = ref()
const alreadyActions = ref(false)

const footer = createResource({
  url: 'go1_cms.api.footer.get_info_footer_component',
  auto: true,
  transform: (data) => {
    _footer.value = JSON.parse(JSON.stringify(data))
    alreadyActions.value = true
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
const dirty = computed(() => {
  if(JSON.stringify(_footer.value) == '{}'){
    return false
  }
  return JSON.stringify(footer.data) !== JSON.stringify(_footer.value)
})

async function callUpdateDoc() {
  changeLoadingValue(true, 'Đang lưu...')
  try {
    let data = JSON.parse(JSON.stringify(_footer.value))

    // upload image
    await handleUploadFieldImage(
      data,
      _footer,
      'Footer Component',
      _footer.value.docname,
    )

    let docUpdate = await call(
      'go1_cms.api.footer.update_info_footer_component',
      {
        data: data,
      },
    )

    if (docUpdate.name) {
      footer.reload()

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
  await footer.reload()
}
</script>
