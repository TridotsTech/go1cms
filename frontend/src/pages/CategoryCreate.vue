<template>
  <LayoutHeader>
    <template #left-header>
      <Breadcrumbs :items="breadcrumbs" />
    </template>
  </LayoutHeader>
  <div class="p-6 mt-12">
    <div class="border-b mb-4 pb-2 border-gray-300">
      <div class="flex flex-wrap justify-between items-center gap-2">
        <h2 class="font-bold text-3xl">Thêm mới danh mục bài viết</h2>
      </div>
    </div>
    <div class="p-4 border border-gray-300 rounded-sm mb-4">
      <div>
        <div class="p-2 grid grid-cols-2 gap-4">
          <div class="flex flex-col gap-4">
            <FormControl
              :type="'text'"
              size="md"
              variant="subtle"
              placeholder="Nhập tên danh mục"
              label="Tiêu danh mục"
              v-model="inputValue"
            />
            <FormControl
              :type="'textarea'"
              size="md"
              variant="subtle"
              placeholder="Nhập mô tả"
              label="Mô tả"
              v-model="inputValue"
              rows="10"
            />
          </div>
        </div>
      </div>
    </div>
    <div class="flex p-4 border border-gray-300 rounded-sm gap-2 justify-end">
      <Button
        :variant="'subtle'"
        theme="gray"
        size="md"
        label="Hủy"
        route="/category"
      ></Button>
      <Button :variant="'solid'" theme="blue" size="md" label="Lưu"></Button>
    </div>
  </div>
</template>

<script setup>
import LayoutHeader from '@/components/LayoutHeader.vue'
import { Breadcrumbs, FormControl } from 'frappe-ui'
const breadcrumbs = [
  { label: 'Quản lý danh mục', route: { name: 'Category' } },
  { label: 'Thêm mới danh mục bài viết', route: { name: 'Category Create' } },
]
</script>
