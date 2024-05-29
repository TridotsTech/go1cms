<template>
  <LayoutHeader>
    <template #left-header>
      <Breadcrumbs :items="breadcrumbs" />
    </template>
  </LayoutHeader>
  <div class="p-6 overflow-auto">Forms</div>
</template>

<script setup>
import LayoutHeader from '@/components/LayoutHeader.vue'
import { Breadcrumbs } from 'frappe-ui'
const breadcrumbs = [{ label: 'Quản lý biểu mẫu', route: { name: 'Forms' } }]
</script>
