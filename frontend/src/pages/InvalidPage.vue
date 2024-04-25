<template>
  <div
    class="grid h-full place-items-center px-4 py-20 text-center text-lg text-gray-600"
  >
    <div class="space-y-2">
      <div>Trang không hợp lệ hoặc không được phép truy cập</div>
      <Button :route="{ name: 'My Website' }">
        <template #prefix><MyWebsiteIcon class="w-4 h-4" /></template>
        Website của tôi
      </Button>
    </div>
  </div>
</template>

<script setup>
import MyWebsiteIcon from '@/components/Icons/MyWebsiteIcon.vue'
</script>
