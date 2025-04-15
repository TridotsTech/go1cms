<template>
  <LayoutHeader>
    <template #left-header>
      <Breadcrumbs :items="breadcrumbs" />
    </template>
    <template #right-header>
      <div class="flex rounded-sm gap-2 justify-end">
        <Button
          variant="subtle"
          theme="gray"
          size="md"
          :label="__('Cancel')"
          route="/categories"
        ></Button>
        <Button
          variant="solid"
          theme="blue"
          size="md"
          :label="__('Save')"
          @click="callInsertDoc"
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
    <div class="p-4 border border-gray-300 rounded-sm mb-4">
      <div class="mb-5">
        <Fields :sections="sections" :data="_category" />
      </div>
    </div>
  </div>
</template>

<script setup>
import Fields from '@/components/Fields.vue'
import LayoutHeader from '@/components/LayoutHeader.vue'
import { Breadcrumbs, call, ErrorMessage } from 'frappe-ui'
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { createToast, errorMessage, validErrApi } from '@/utils'
import { globalStore } from '@/stores/global'
const { changeLoadingValue } = globalStore()

const router = useRouter()
const breadcrumbs = [
  { label: __('Category management'), route: { name: 'Categories' } },
  { label: __('Add New'), route: { name: 'Category Create' } },
]

let _category = ref({})
const msgError = ref()

const sections = computed(() => {
  return [
    {
      section: 'sec 1',
      columns: 1,
      class: 'md:grid-cols-2',
      fields: [
        {
          label: 'Category name',
          mandatory: true,
          name: 'category_title',
          type: 'data',
          placeholder: 'Enter name',
        },
      ],
    },
    {
      section: 'sec 2',
      columns: 2,
      hideBorder: true,
      fields: [
        {
          label: 'Description',
          name: 'description',
          type: 'textarea',
          placeholder: 'Enter',
          rows: 10,
        },
      ],
    },
  ]
})

async function callInsertDoc() {
  msgError.value = null

  const regex = /[&\/\\#+()$~%.`'":*?<>{}]/g
  if (regex.test(_category.value.category_title)) {
    msgError.value = `${__('Category name must not contain special characters:')} [&\/\\#+()$~%.\`'":*?<>{}]`
    return false
  }

  changeLoadingValue(true, __('Saving...'))
  try {
    const doc = await call('go1_cms.api.category.create_category', {
      data: {
        ..._category.value,
      },
    })
    createToast({
      title: __('Saved'),
      icon: 'check',
      iconClasses: 'text-green-600',
    })
    doc.name &&
      router.push({
        name: 'Category Detail',
        params: { categoryId: doc.name },
      })
  } catch (err) {
    validErrApi(err, router)
    msgError.value = err.messages.join(', ')
    errorMessage(__('An error has occurred'), err.messages.join(', '))
  }
  changeLoadingValue(false)
}
</script>
