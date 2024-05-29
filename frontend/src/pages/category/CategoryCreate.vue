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
          label="Hủy"
          route="/category"
        ></Button>
        <Button
          variant="solid"
          theme="blue"
          size="md"
          label="Lưu"
          @click="callInsertDoc"
        ></Button>
      </div>
    </template>
  </LayoutHeader>
  <div class="p-6 overflow-auto">
    <div v-if="msgError" class="p-4 border border-gray-300 rounded-sm mb-4">
      <div class="text-base text-red-600 font-bold mb-2">Có lỗi xảy ra:</div>
      <ErrorMessage :message="msgError" />
    </div>
    <div class="p-6 border border-gray-300 rounded-sm mb-4">
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
import { createToast, errorMessage } from '@/utils'
import { globalStore } from '@/stores/global'
const { changeLoadingValue } = globalStore()

const router = useRouter()
const breadcrumbs = [
  { label: 'Quản lý danh mục', route: { name: 'Category' } },
  { label: 'Thêm mới danh mục bài viết', route: { name: 'Category Create' } },
]

let _category = ref({})
const msgError = ref()

const sections = computed(() => {
  return [
    {
      section: 'Category Name',
      columns: 1,
      class: 'md:grid-cols-2',
      fields: [
        {
          label: 'Tiêu đề',
          mandatory: true,
          name: 'category_title',
          type: 'data',
          placeholder: 'Nhập tiêu đề',
        },
      ],
    },
    {
      section: 'Description',
      columns: 2,
      hideBorder: true,
      fields: [
        {
          label: 'Mô tả',
          name: 'description',
          type: 'textarea',
          placeholder: 'Nhập mô tả',
          rows: 10,
        },
      ],
    },
  ]
})

async function callInsertDoc() {
  changeLoadingValue(true, 'Đang lưu...')
  try {
    const doc = await call('go1_cms.api.category.create_category', {
      data: {
        ..._category.value,
      },
    })
    createToast({
      title: 'Thêm mới thành công',
      icon: 'check',
      iconClasses: 'text-green-600',
    })
    doc.name &&
      router.push({
        name: 'Category Detail',
        params: { categoryId: doc.name },
      })
  } catch (err) {
    msgError.value = err.messages.join(', ')
    errorMessage('Có lỗi xảy ra', err.messages.join(', '))
  }
  changeLoadingValue(false)
}
</script>
