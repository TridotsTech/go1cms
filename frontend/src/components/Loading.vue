<template>
  <div
    v-if="loadingValue.active"
    class="flex flex-1 flex-col w-full h-full absolute items-center justify-center text-xl font-medium text-red-500 z-50"
  >
    <div class="absolute w-full h-full opacity-80 bg-gray-400"></div>
    <div class="z-[100] flex flex-col items-center gap-3">
      <LoadingIndicator class="h-6 w-6" />
      <span>{{ loadingValue.text }}</span>
    </div>
  </div>
</template>

<script setup>
import { storeToRefs } from 'pinia'
import { globalStore } from '@/stores/global'
const { loadingValue } = storeToRefs(globalStore())
</script>
