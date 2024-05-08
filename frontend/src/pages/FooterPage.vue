<template>
  <LayoutHeader>
    <template #left-header>
      <Breadcrumbs :items="breadcrumbs" />
    </template>
  </LayoutHeader>
  <div class="p-6">Footer Page</div>
</template>

<script setup>
import LayoutHeader from '@/components/LayoutHeader.vue'
import { Breadcrumbs } from 'frappe-ui'
const breadcrumbs = [{ label: 'Trang Footer', route: { name: 'Footer Page' } }]
</script>
