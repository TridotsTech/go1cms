<template>
  <div v-bind="{ opened, toggle }">
    <div
      class="flex h-7 max-w-fit cursor-pointer items-center gap-2 pr-3 text-base font-semibold leading-5 mb-2"
      @click="toggle()"
    >
      {{ label || 'Untitled' }}
      <FeatherIcon
        name="chevron-right"
        class="h-4 text-gray-900 transition-all duration-300 ease-in-out"
        :class="{ 'rotate-90': opened }"
      />
    </div>
    <div class="px-2">
      <slot v-if="opened" name="content"></slot>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { FeatherIcon } from 'frappe-ui'
const props = defineProps({
  label: {
    type: String,
    default: '',
  },
  isOpened: {
    type: Boolean,
    default: false,
  },
})
function toggle() {
  opened.value = !opened.value
}

let opened = ref(props.isOpened)
</script>
