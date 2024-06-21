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
    <div
      v-if="_webSetup?.fields_cp && _webSetup?.fields_cp.length"
      class="p-4 border border-gray-300 rounded-sm mb-4"
    >
      <div class="p-2">
        <div class="mb-4">
          <h2 class="font-bold text-xl">Thông tin chung</h2>
        </div>
        <div v-for="(field, idx) in _webSetup?.fields_cp" :key="field.name">
          <div v-if="field.allow_edit" class="border-t py-4">
            <div class="mb-4">
              <h2 class="font-bold text-lg">{{ field.section_title }}</h2>
            </div>
            <div class="grid grid-cols-1 lg:grid-cols-2 gap-4">
              <template v-for="fd in field.fields">
                <template v-if="fd.group_name">
                  <div class="lg:col-span-2">
                    <div class="grid grid-cols-1 lg:grid-cols-2 gap-4">
                      <template v-for="fsc in fd.fields">
                        <FieldSection
                          :field="fsc"
                          :sectionName="field.section_title"
                        ></FieldSection>
                      </template>
                    </div>
                  </div>
                </template>
                <template v-else>
                  <FieldSection
                    :field="fd"
                    :sectionName="field.section_title"
                  ></FieldSection>
                </template>
              </template>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import LayoutHeader from '@/components/LayoutHeader.vue'
import FieldSection from '../components/FieldSection.vue'
import { Breadcrumbs, ErrorMessage, createResource, call } from 'frappe-ui'
import { ref, computed, watch } from 'vue'
import { createToast, errorMessage, uploadFile } from '@/utils'
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
    for (const [idx_cp, field] of _webSetup.value.fields_cp.entries()) {
      for (const [idx_f, f] of field.fields.entries()) {
        if (f.group_name) {
          for (const [idx, f_st] of f.fields.entries()) {
            if (f_st.field_type == 'Attach' && f_st.upload_file_image) {
              // upload file
              let file_url = await uploadFile(
                'Web Theme',
                _webSetup.value.docname,
                f_st.field_key,
                f_st.content,
                f_st.upload_file_image,
              )
              data['fields_cp'][idx_cp]['fields'][idx_f]['fields'][idx][
                'content'
              ] = file_url
            }
          }
        } else {
          if (f.field_type == 'Attach' && f.upload_file_image) {
            // upload file
            let file_url = await uploadFile(
              'Web Theme',
              _webSetup.value.docname,
              f.field_key,
              f.content,
              f.upload_file_image,
            )
            data['fields_cp'][idx_cp]['fields'][idx_f]['content'] = file_url
          }
        }
      }
    }

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

async function cacelSaveDoc() {
  await webSetup.reload()
}
</script>
