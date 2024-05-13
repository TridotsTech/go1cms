<template>
  <LayoutHeader>
    <template #left-header>
      <Breadcrumbs :items="breadcrumbs" />
    </template>
  </LayoutHeader>
  <div class="p-6 mt-12">
    <div class="border-b pb-2 mb-4 border-gray-300">
      <div>
        <h2 class="font-bold text-3xl">Chân trang</h2>
      </div>
    </div>
    <div class="p-4 border border-gray-300 rounded-sm mb-4">
      <div class="p-2">
        <div class="mb-4">
          <h2 class="font-bold text-xl">Nội dung bản quyền</h2>
        </div>
        <div class="grid lg:grid-cols-2 gap-4">
          <div class="flex flex-col gap-4">
            <FormControl
              type="textarea"
              size="md"
              variant="subtle"
              placeholder="Nhập nội dung"
              label="Nội dung"
              v-model="inputValue"
              rows="7"
            />
          </div>
        </div>
        <div class="flex mt-4 border-t py-2 rounded-sm gap-2 justify-end">
          <Button
            :variant="'solid'"
            theme="blue"
            size="md"
            label="Lưu"
          ></Button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import LayoutHeader from '@/components/LayoutHeader.vue'
import { Breadcrumbs, FormControl, ErrorMessage } from 'frappe-ui'
import { ref, onMounted } from 'vue'

const breadcrumbs = [{ label: 'Chân trang', route: { name: 'Footer Page' } }]
</script>
