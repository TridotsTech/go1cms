<template>
  <Teleport to="#app-header" v-if="showHeader">
    <header
      class="flex flex-wrap justify-between items-center px-5 py-2.5 min-h-14"
    >
      <div>
        <slot name="left-header" />
      </div>
      <div>
        <slot name="right-header" />
      </div>
    </header>
  </Teleport>
</template>
<script setup>
import { ref, nextTick } from 'vue'

const showHeader = ref(false)

nextTick(() => {
  showHeader.value = true
})
</script>
