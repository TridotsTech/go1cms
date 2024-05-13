<template>
  <LayoutHeader>
    <template #left-header>
      <Breadcrumbs :items="breadcrumbs" />
    </template>
  </LayoutHeader>
  <div class="p-6 mt-12">
    <div class="text-center mt-10">
      <div>
        Bạn chưa có website nào, hãy nhấp vào "Xem kho giao diện" và chọn một
        mẫu để tạo website riêng của bạn.
      </div>
      <Button
        class="my-5"
        :variant="'solid'"
        theme="gray"
        size="sm"
        label="Xem kho giao diện"
        route="/interface-repository"
      >
      </Button>
    </div>
  </div>
</template>

<script setup>
import LayoutHeader from '@/components/LayoutHeader.vue'
import { Breadcrumbs } from 'frappe-ui'
let title = 'Interface'
const breadcrumbs = [{ label: title, route: { name: 'Interface' } }]
</script>
