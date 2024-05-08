<template>
  <LayoutHeader>
    <template #left-header>
      <Breadcrumbs :items="breadcrumbs" />
    </template>
  </LayoutHeader>
  <div class="p-6">New Page</div>
</template>

<script setup>
import LayoutHeader from '@/components/LayoutHeader.vue'
import { Breadcrumbs } from 'frappe-ui'
let title = 'New Page'
const breadcrumbs = [{ label: title, route: { name: 'New Page' } }]
</script>
