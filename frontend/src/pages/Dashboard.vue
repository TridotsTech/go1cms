<template>
  <LayoutHeader>
    <template #left-header>
      <Breadcrumbs :items="breadcrumbs" />
    </template>
  </LayoutHeader>
  <div class="p-6 overflow-auto">Dashboard</div>
</template>

<script setup>
import LayoutHeader from '@/components/LayoutHeader.vue'
import { Breadcrumbs } from 'frappe-ui'
let title = 'Dashboard'
const breadcrumbs = [{ label: title, route: { name: 'Dashboard' } }]
</script>
