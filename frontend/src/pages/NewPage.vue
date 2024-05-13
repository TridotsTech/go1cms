<template>
  <LayoutHeader>
    <template #left-header>
      <Breadcrumbs :items="breadcrumbs" />
    </template>
  </LayoutHeader>
  <div class="p-6 mt-12">
    <div class="border-b pb-2 mb-4 border-gray-300">
      <div>
        <h2 class="font-bold text-3xl">Trang mới</h2>
      </div>
    </div>
    <div class="p-4 border border-gray-300 rounded-sm mb-4">
      <div class="p-2"></div>
    </div>
  </div>
</template>

<script setup>
import LayoutHeader from '@/components/LayoutHeader.vue'
import { Breadcrumbs } from 'frappe-ui'
const breadcrumbs = [{ label: 'Trang mới', route: { name: 'New Page' } }]
</script>
