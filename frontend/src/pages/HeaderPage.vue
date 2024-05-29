<template>
  <LayoutHeader>
    <template #left-header>
      <Breadcrumbs :items="breadcrumbs" />
    </template>
  </LayoutHeader>
  <div class="p-6 overflow-auto">
    <div class="p-4 border border-gray-300 rounded-sm mb-4">
      <div class="p-2">
        <div class="mb-4">
          <h2 class="font-bold text-xl">Nút 1</h2>
        </div>
        <div class="grid lg:grid-cols-2 gap-4">
          <div class="flex flex-col gap-4">
            <FormControl
              :type="'text'"
              size="md"
              variant="subtle"
              placeholder="Nhập nội dung"
              label="Nội dung nút"
              v-model="inputValue"
            />
            <FormControl
              type="select"
              :options="[
                {
                  label: 'Mở tại trang',
                  value: '_self',
                },
                {
                  label: 'Mở trang mới',
                  value: '_blank',
                },
              ]"
              size="sm"
              variant="subtle"
              placeholder="Liên kết mục"
              label="Liên kết mục"
              v-model="selectValue"
            />
          </div>
          <div class="flex flex-col gap-4">
            <FormControl
              :type="'text'"
              size="md"
              variant="subtle"
              placeholder="Nhập Link"
              label="Link"
              v-model="inputValue"
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

const breadcrumbs = [{ label: 'Đầu trang', route: { name: 'Header Page' } }]
const selectValue = ref()
</script>
