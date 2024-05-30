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
      v-if="_header?.fields_cp && _header?.fields_cp.length"
      class="p-4 border border-gray-300 rounded-sm mb-4"
    >
      <div class="p-2">
        <div v-for="(field, idx) in _header?.fields_cp" :key="field.name">
          <div
            v-if="field.allow_edit"
            :class="idx != 0 ? 'border-t py-4' : 'pb-4'"
          >
            <div class="mb-4">
              <h2 class="font-bold text-xl">{{ field.label }}</h2>
            </div>
            <div class="grid lg:grid-cols-2 gap-4">
              <template v-for="fd in field.fields">
                <FieldSection :field="fd"></FieldSection>
              </template>
            </div>
          </div>
        </div>
      </div>
    </div>
    <div
      v-if="_header?.fields_st_cp && _header?.fields_st_cp.length"
      class="p-4 border border-gray-300 rounded-sm mb-4"
    >
      <div class="p-2">
        <div class="mb-4">
          <h2 class="font-bold text-xl">Các thành phần của trang</h2>
        </div>
        <div v-for="(field, idx) in _header?.fields_st_cp" :key="field.name">
          <div
            v-if="field.allow_edit"
            :class="idx != 0 ? 'border-t py-4' : 'pb-4'"
          >
            <div class="mb-2">
              <h2 class="font-bold text-lg">{{ field.section_title }}</h2>
            </div>
            <div class="grid lg:grid-cols-2 gap-4">
              <template v-for="fd in field.fields">
                <template v-if="fd.group_name">
                  <template v-for="fsc in fd.fields">
                    <FieldSection
                      :field="fsc"
                      :sectionName="field.section_title"
                    ></FieldSection>
                  </template>
                </template>
                <template v-else>
                  <FieldSection
                    :field="fd"
                    :sectionName="field.section_title"
                  ></FieldSection>
                </template>
              </template>
              <template v-for="fd in field.fields_ps">
                <FieldSection :field="fd"></FieldSection>
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
import { createToast, errorMessage } from '@/utils'
import { globalStore } from '@/stores/global'
const { changeLoadingValue } = globalStore()

const breadcrumbs = [{ label: 'Đầu trang', route: { name: 'Header Page' } }]
const _header = ref({})
const msgError = ref()

const header = createResource({
  url: 'go1_cms.api.header.get_info_header_component',
  auto: true,
  transform: (data) => {
    _header.value = JSON.parse(JSON.stringify(data))
    return data
  },
})

// handle allow actions
const alreadyActions = ref(false)
const dirty = computed(() => {
  return JSON.stringify(header.data) !== JSON.stringify(_header.value)
})

watch(dirty, (val) => {
  alreadyActions.value = true
})

async function callUpdateDoc() {
  changeLoadingValue(true, 'Đang lưu...')
  try {
    let data = JSON.parse(JSON.stringify(_header.value))

    // upload image
    for (const [idx_cp, field] of _header.value.fields_cp.entries()) {
      for (const [idx, f] of field.fields.entries()) {
        if (f.field_type == 'Attach' && f.upload_file_image) {
          // upload file
          let file_url = await uploadFile(
            'Header Component',
            _header.value.docname,
            f.field_key,
            f.content,
            f.upload_file_image
          )

          data['fields_cp'][idx_cp]['fields'][idx]['content'] = file_url
        }
      }
    }

    for (const [idx_cp, field] of _header.value.fields_st_cp.entries()) {
      for (const [idx_f, f] of field.fields.entries()) {
        if (f.group_name) {
          for (const [idx, f_st] of f.fields.entries()) {
            if (f_st.field_type == 'Attach' && f_st.upload_file_image) {
              // upload file
              let file_url = await uploadFile(
                'Header Component',
                _header.value.docname,
                f_st.field_key,
                f_st.content,
                f_st.upload_file_image
              )

              data['fields_st_cp'][idx_cp]['fields'][idx_f]['fields'][idx][
                'content'
              ] = file_url
            }
          }
        } else {
          if (f.field_type == 'Attach' && f.upload_file_image) {
            // upload file
            let file_url = await uploadFile(
              'Header Component',
              _header.value.docname,
              f.field_key,
              f.content,
              f.upload_file_image
            )

            data['fields_st_cp'][idx_cp]['fields'][idx_f]['content'] = file_url
          }
        }
      }
    }

    let docUpdate = await call(
      'go1_cms.api.header.update_info_header_component',
      {
        data: data,
      }
    )

    if (docUpdate.name) {
      header.reload()

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

async function uploadFile(
  doctype,
  docname,
  fieldname,
  file_url_old,
  upload_file_image
) {
  let file_url = ''
  let headers = { Accept: 'application/json' }
  if (window.csrf_token && window.csrf_token !== '{{ csrf_token }}') {
    headers['X-Frappe-CSRF-Token'] = window.csrf_token
  }

  let imgForm = new FormData()
  imgForm.append('file', upload_file_image, upload_file_image.name)
  imgForm.append('is_private', 0)
  imgForm.append('doctype', doctype)
  imgForm.append('fieldname', fieldname)
  imgForm.append('docname', docname)
  imgForm.append('file_url_old', file_url_old)

  await fetch('/api/method/go1_cms.api.handler_file.upload_file', {
    headers: headers,
    method: 'POST',
    body: imgForm,
  })
    .then((res) => res.json())
    .then((data) => {
      if (data.message) {
        file_url = data.message.file_url
      }
    })
    .catch((err) => {
      if (err.messages && err.messages.length) {
        msgError.value = err.messages.join(', ')
        errorMessage('Có lỗi xảy ra', err.messages.join(', '))
      } else {
        errorMessage('Có lỗi xảy ra', err)
      }
    })

  return file_url
}

async function cacelSaveDoc() {
  await header.reload()
}
</script>
