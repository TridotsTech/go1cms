<template>
  <div
    class="flex flex-col gap-2 min-h-24 w-full shadow-lg rounded-lg p-4"
    :style="customStyle"
  >
    <p class="text-base">{{ title }}</p>
    <h5 class="text-xl font-bold">
      {{ formatNumber(value) || '0' }}
    </h5>
    <Popover trigger="hover" :hoverDelay="0.5">
      <template #target>
        <div
          v-if="typeCompare"
          class="flex items-end"
          :class="valuePercent >= 0 ? 'text-[#188038FF]' : 'text-red-600'"
        >
          <ArrowUpIcon v-if="valuePercent >= 0" class="h-3.5"></ArrowUpIcon>
          <ArrowDownIcon v-else class="h-3.5"></ArrowDownIcon>

          <span class="text-sm"> {{ formatNumber(valuePercent) || 0 }}% </span>
        </div>
      </template>
      <template #body-main>
        <div class="p-2">
          <div class="flex flex-col gap-2">
            <div class="text-sm">
              <span
                :class="valuePercent >= 0 ? 'text-[#188038FF]' : 'text-red-600'"
              >
                {{ valuePercent >= 0 ? 'Tăng' : 'Giảm' }}
                {{ formatNumber(valuePercent) }}%
              </span>
              <span> so với kỳ trước </span>
            </div>
            <div class="text-base flex flex-col gap-2">
              <div>
                {{ labelCompare[0] }}:
                <span class="font-bold">{{ formatNumber(value) }}</span>
              </div>
              <div>
                {{ labelCompare[1] }}:
                <span class="font-bold">{{ formatNumber(valuePrevious) }}</span>
              </div>
            </div>
          </div>
        </div>
      </template>
    </Popover>
  </div>
</template>

<script setup>
import ArrowDownIcon from '@/components/Icons/ArrowDownIcon.vue'
import ArrowUpIcon from '@/components/Icons/ArrowUpIcon.vue'
import { Popover } from 'frappe-ui'
import { formatNumber } from '@/utils'

const props = defineProps({
  title: {
    type: String,
    default: '',
  },
  customStyle: {
    type: Object,
    default: {},
  },
  value: {
    type: Number,
    default: 0,
  },
  valuePrevious: {
    type: Number,
    default: 0,
  },
  labelCompare: {
    type: Array,
    default: [null, null],
  },
  valuePercent: {
    type: Number,
    default: 0,
  },
  typeCompare: {
    type: Boolean,
    default: true,
  },
})
</script>
