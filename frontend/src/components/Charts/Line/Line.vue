<script setup>
import BaseChart from '@/components/Charts/BaseChart.vue'
import { computed } from 'vue'

const props = defineProps({
  options: { type: Object, required: true },
})

const lineChartOptions = computed(() => {
  var series = []
  var rows = props.options.rows
  var colors = props.options.colors
  var data = props.options.data

  if (Array.isArray(rows)) {
    for (let i = 0; i < rows.length; i++) {
      if (i == 0) {
        series.push({
          name: rows[i],
          type: 'line',
          data: data[i],
          color: colors[i],
        })
      } else {
        series.push({
          name: rows[i],
          type: 'line',
          data: data[i],
          color: colors[i],
          lineStyle: {
            type: 'dashed',
          },
        })
      }
    }
  }

  return {
    title: {},
    tooltip: {
      trigger: 'axis',
      formatter: function (params) {
        let html = ''
        if (params.length == 1) {
          html = `
                <div class="flex mb-2">
                    <div class="mt-2" style="width: 20px; border-top: 3px solid ${params[0].color}; margin-right: 10px;"></div>
                    <div>
                      <div>${params[0].name}</div>
                      <div class="text-gray-800 text-xl font-extrabold">${params[0].value}</div>
                    </div>
                </div>
            `
        } else if (params.length == 2) {
          html = `
                <div class="flex mb-2">
                    <div class="mt-2" style="width: 20px; border-top: 3px solid ${params[0].color}; margin-right: 10px;"></div>
                    <div>
                      <div>${params[0].name}</div>
                      <div class="text-gray-800 text-xl font-extrabold">${params[0].value}</div>
                    </div>
                </div>
                <div class="flex mb-2">
                    <div class="mt-2" style="width: 20px; border-top: 3px dashed ${params[1].color}; margin-right: 10px;"></div>
                    <div>
                      <div>${params[1].name}</div>
                      <div class="text-gray-800 text-xl font-extrabold">${params[1].value}</div>
                    </div>
                </div>
            `
        }
        return html
      },
    },
    legend: {
      data: rows,
      bottom: 0,
      itemWidth: 60,
      itemHeight: 10,
      padding: [5, 10],
      itemGap: 20,
    },
    grid: {
      left: 25,
      right: 35,
      bottom: 60,
      containLabel: true,
    },
    toolbox: {
      feature: {
        saveAsImage: {},
      },
    },
    xAxis: {
      type: 'category',
      boundaryGap: false,
      data: props.options.columns,
      axisLabel: {
        fontFamily: 'inherit',
      },
    },
    yAxis: {
      type: 'value',
      axisLabel: {
        fontFamily: 'inherit',
      },
    },
    series: series,
  }
})
</script>

<template>
  <BaseChart :title="props.options.title" :options="lineChartOptions" />
</template>
