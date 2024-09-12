<template>
  <Teleport to="#app-header" v-if="showHeader">
    <header
      class="flex flex-wrap justify-between items-center px-5 py-2.5 min-h-14"
    >
      <div class="header_left">
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
<style>
.header_left > div > div {
  flex-wrap: wrap;
  white-space: normal;
}
</style>
