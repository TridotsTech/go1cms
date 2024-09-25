<template>
  <div class="h-screen">
    <div
      class="flex inset-0 justify-center h-2/3 place-items-center px-4 py-20 text-center text-lg text-gray-600"
    >
      <div class="space-y-2">
        <div class="flex justify-center">
          <AccessDeniedIcon class="w-10 h-10"></AccessDeniedIcon>
        </div>
        <div class="font-medium">Trang không hợp lệ</div>
        <Button :route="{ name: 'Interface Repository' }">
          <template #prefix><ArrowUpRightIcon class="w-4 h-4" /></template>
          Kho giao diện
        </Button>
      </div>
    </div>
  </div>
</template>

<script setup>
import ArrowUpRightIcon from '@/components/Icons/ArrowUpRightIcon.vue'
import AccessDeniedIcon from '@/components/Icons/AccessDeniedIcon.vue'
</script>
