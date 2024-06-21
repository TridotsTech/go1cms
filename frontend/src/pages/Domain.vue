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
      v-if="_domain?.fields_cp && _domain?.fields_cp.length"
      class="p-4 border border-gray-300 rounded-sm mb-4"
    >
      <div class="p-2">
        <div class="mb-4">
          <h2 class="font-bold text-xl">Thông tin chung</h2>
        </div>
        <div v-for="(field, idx) in _domain?.fields_cp" :key="field.name">
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

const breadcrumbs = [{ label: 'Cấu hình tên miền', route: { name: 'Domain' } }]
const _domain = ref({})
const msgError = ref()

// get detail
const domain = createResource({
  url: 'go1_cms.api.domain.get_info_domain',
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

    _domain.value = JSON.parse(JSON.stringify(data))
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
  if (_domain.value?.fields_cp) {
    let allow_edit = false
    if (_domain.value?.fields_cp[0].fields[0].content) {
      allow_edit = true
    }
    _domain.value.fields_cp[0].fields[1].allow_edit = allow_edit
  }
  return JSON.stringify(domain.data) !== JSON.stringify(_domain.value)
})

watch(dirty, (val) => {
  alreadyActions.value = true
})

async function callUpdateDoc() {
  changeLoadingValue(true, 'Đang lưu...')
  try {
    let data = JSON.parse(JSON.stringify(_domain.value))

    let docUpdate = await call('go1_cms.api.domain.update_info_domain', {
      data: data,
    })

    if (docUpdate.name) {
      domain.reload()

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
  await domain.reload()
}
</script>
