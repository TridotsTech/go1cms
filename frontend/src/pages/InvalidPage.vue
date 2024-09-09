<template>
  <div
    class="grid h-full place-items-center px-4 py-20 text-center text-lg text-gray-600"
  >
    <div class="space-y-2">
      <div>Trang không hợp lệ hoặc không được phép truy cập</div>
      <Button :route="{ name: 'Interface Repository' }">
        <template #prefix><DisplayIcon class="w-4 h-4" /></template>
        Kho giao diện
      </Button>
    </div>
  </div>
</template>

<script setup>
import DisplayIcon from '@/components/Icons/DisplayIcon.vue'
</script>
