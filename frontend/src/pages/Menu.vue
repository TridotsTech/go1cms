<template>
  <LayoutHeader>
    <template #left-header>
      <Breadcrumbs :items="breadcrumbs" />
    </template>
  </LayoutHeader>
  <div class="p-6 overflow-auto">
    <div class="pb-4">
      <MenuListView
        class="min-h-[250px] max-h-[80vh]"
        v-model:loading="loading"
        :rows="dataRows"
        :columns="dataColums"
        :options="{
          selectable: false,
          showTooltip: false,
          resizeColumn: true,
          emptyState: {
            title: 'Giao diện hiện tại không có menu nào',
            description:
              'Bạn có thể tùy chỉnh hiển thị khi giao diện có các menu',
          },
        }"
        @reFresh="
          () => {
            reFresh = !reFresh
          }
        "
      ></MenuListView>
    </div>
  </div>
</template>

<script setup>
import LayoutHeader from '@/components/LayoutHeader.vue'
import { Breadcrumbs } from 'frappe-ui'
import MenuListView from '@/components/ListViews/MenuListView.vue'
import { ref, watch } from 'vue'

const breadcrumbs = [{ label: 'Menu', route: { name: 'Menu' } }]
const reFresh = ref(true)
const dataRows = ref([])
const dataColums = ref([
  {
    label: 'STT',
    key: 'stt',
    width: '50px',
  },
  {
    label: 'Menu',
    key: 'name_web',
  },
  {
    label: 'Hành dộng',
    key: 'action',
  },
])
</script>
