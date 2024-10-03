<template>
  <div class="h-screen">
    <div
      class="flex justify-center h-2/3 place-items-center px-4 py-20 text-center text-lg text-gray-600"
    >
      <div class="space-y-2">
        <div class="flex justify-center">
          <AccessDeniedIcon class="w-10 h-10"></AccessDeniedIcon>
        </div>
        <div class="font-medium">Trang không được phép truy cập.</div>
        <div class="text-base">
          Nếu bạn là quản trị viên, hãy nhấp vào nút bên dưới để thay đổi tài
          khoản.
        </div>
        <Button @click="logout.submit()">
          <template #prefix><RefreshIcon class="w-4 h-4" /></template>
          Đổi tài khoản
        </Button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { sessionStore } from '@/stores/session'
const { logout } = sessionStore()

import AccessDeniedIcon from '@/components/Icons/AccessDeniedIcon.vue'
import RefreshIcon from '@/components/Icons/RefreshIcon.vue'
</script>
