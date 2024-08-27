<script setup>
import BaseChart from '@/components/Charts/BaseChart.vue'
import { computed } from 'vue'
import { formatNumber } from '@/utils'

const props = defineProps({
  options: { type: Object, required: true },
})

const lineChartOptions = computed(() => {
  var series = []
  var colors = props.options.colors
  var data = props.options.data

  if (Array.isArray(colors)) {
    for (let i = 0; i < colors.length; i++) {
      series.push({
        realtimeSort: i == 0 ? true : false,
        type: 'bar',
        data: data[i],
        color: colors[i],
        emphasis: {
          focus: 'series',
        },
      })
    }
  }
  return {
    title: {},
    tooltip: {
      trigger: 'axis',
      formatter: function (params) {
        let data = params[0]
        let html = `
          <div class="font-bold">${data.axisValue}</div>
          <div>Số lượt xem: <span class="font-bold">${data.value}</span></div>
        `
        if (data?.data.compare != undefined) {
          let arrow = ''
          if (data?.data.compare >= 0) {
            arrow = `<div class="flex items-center text-[#188038FF]"><svg class="h-3" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <g id="SVGRepo_bgCarrier" stroke-width="0"></g>
            <g
              id="SVGRepo_tracerCarrier"
              stroke-linecap="round"
              stroke-linejoin="round"
            ></g>
            <g id="SVGRepo_iconCarrier">
              <path
                d="M7.33199 7.68464C6.94146 8.07517 6.3083 8.07517 5.91777 7.68464C5.52725 7.29412 5.52725 6.66095 5.91777 6.27043L10.5834 1.60483C11.3644 0.823781 12.6308 0.82378 13.4118 1.60483L18.0802 6.27327C18.4707 6.66379 18.4707 7.29696 18.0802 7.68748C17.6897 8.078 17.0565 8.078 16.666 7.68748L13 4.02145V21.9999C13 22.5522 12.5523 22.9999 12 22.9999C11.4477 22.9999 11 22.5522 11 21.9999V4.01666L7.33199 7.68464Z"
                fill="currentColor"
              ></path>
            </g>
          </svg>${formatNumber(data?.data.compare)}%</div>`
          } else {
            arrow = `<div class="flex items-center text-red-600"><svg class="h-3" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <g id="SVGRepo_bgCarrier" stroke-width="0"></g>
            <g
              id="SVGRepo_tracerCarrier"
              stroke-linecap="round"
              stroke-linejoin="round"
            ></g>
            <g id="SVGRepo_iconCarrier">
              <path
                d="M7.33199 16.3154C6.94146 15.9248 6.3083 15.9248 5.91777 16.3154C5.52725 16.7059 5.52725 17.339 5.91777 17.7296L10.5834 22.3952C11.3644 23.1762 12.6308 23.1762 13.4118 22.3952L18.0802 17.7267C18.4707 17.3362 18.4707 16.703 18.0802 16.3125C17.6897 15.922 17.0565 15.922 16.666 16.3125L13 19.9786V2.0001C13 1.44781 12.5523 1.0001 12 1.0001C11.4477 1.0001 11 1.44781 11 2.0001V19.9833L7.33199 16.3154Z"
                fill="currentColor"
              ></path>
            </g>
          </svg>${formatNumber(data?.data.compare)}%</div>`
          }
          html = `
          <div class="flex gap-2">Số lượt xem: <span class="font-bold">${data.value}</span> ${arrow}</div>
          `
        }
        return html
      },
      axisPointer: {
        type: 'shadow',
      },
    },
    legend: {
      show: false,
    },
    grid: {
      left: 25,
      right: 35,
      bottom: 35,
      containLabel: true,
    },
    toolbox: {
      feature: {
        saveAsImage: {},
      },
    },
    xAxis: {
      max: 'dataMax',
      axisLabel: {
        fontFamily: 'inherit',
      },
    },
    yAxis: {
      type: 'category',
      data: props.options.rows,
      inverse: true,
      animationDuration: 300,
      animationDurationUpdate: 300,
      max: 4,
      axisLabel: {
        fontFamily: 'inherit',
        formatter: function (value) {
          const maxLength = 15
          if (value.length > maxLength) {
            return value.substring(0, maxLength) + '...'
          }
          return value
        },
      },
    },

    series: series,
  }
})
</script>

<template>
  <BaseChart :title="props.options.title" :options="lineChartOptions" />
</template>
