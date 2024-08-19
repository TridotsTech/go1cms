<template>
  <LayoutHeader>
    <template #left-header>
      <Breadcrumbs :items="breadcrumbs" />
    </template>
  </LayoutHeader>
  <div class="p-6 overflow-auto">
    <div v-if="msgError" class="p-4 border border-gray-300 rounded-sm mb-4">
      <div class="text-base text-red-600 font-bold mb-2">Có lỗi xảy ra:</div>
      <ErrorMessage :message="msgError" />
    </div>
    <FilterDashboard
      v-model:timeRangeStart="timeRangeStart"
      v-model:timeRangeEnd="timeRangeEnd"
      v-model="filterChange"
      @update="(val) => (selectedCompare = val)"
    ></FilterDashboard>
    <div class="grid grid-cols-1 lg:grid-cols-5 gap-6 mb-8">
      <div class="col-span-1 lg:col-span-4">
        <div class="p-4 border border-gray-300 shadow-2xl rounded-sm">
          <h4 class="mb-4">Phiên truy cập</h4>
          <div>
            <div
              class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6 mb-4"
            >
              <div class="col-span-1">
                <CardDashboard
                  title="Tổng số người dùng"
                  :value="report.data?.rp_range_start.so_nguoi_dung"
                  :valuePrevious="report.data?.rp_range_end?.so_nguoi_dung"
                  :customStyle="{ 'background-color': cardColors[0] }"
                  :valuePercent="infoCompare.ti_le_nguoi_dung"
                  :labelCompare="report.data?.period"
                  :typeCompare="selectedCompare?.value != 'khong_so_sanh'"
                >
                </CardDashboard>
              </div>
              <div class="col-span-1">
                <CardDashboard
                  title="Tổng số phiên truy cập"
                  :value="report.data?.rp_range_start.so_truy_cap"
                  :valuePrevious="report.data?.rp_range_end?.so_truy_cap"
                  :customStyle="{ 'background-color': cardColors[1] }"
                  :valuePercent="infoCompare.ti_le_truy_cap"
                  :labelCompare="report.data?.period"
                  :typeCompare="selectedCompare?.value != 'khong_so_sanh'"
                ></CardDashboard>
              </div>
              <div class="col-span-1">
                <CardDashboard
                  title="Thời gian xem trung bình (s)"
                  :value="report.data?.rp_range_start.thoi_gian_xem_tb"
                  :valuePrevious="report.data?.rp_range_end?.thoi_gian_xem_tb"
                  :customStyle="{ 'background-color': cardColors[2] }"
                  :valuePercent="infoCompare.ti_le_thoi_gian_xem_tb"
                  :labelCompare="report.data?.period"
                  :typeCompare="selectedCompare?.value != 'khong_so_sanh'"
                ></CardDashboard>
              </div>
            </div>
            <Line :options="options.chart_access"></Line>
          </div>
        </div>
      </div>
      <div class="col-span-1 flex flex-col gap-12">
        <div
          class="h-1/2 flex flex-col gap-2 col-span-1 min-h-28 w-full shadow-2xl p-6 justify-center"
          :style="{ 'background-color': cardColors[3] }"
        >
          <p class="text-2xl">Số người truy cập hiện tại</p>
          <h5 class="text-[34px] font-bold">
            {{ formatNumber(report.data?.truy_cap_hien_tai) || '0' }}
          </h5>
        </div>
        <div
          class="h-1/2 flex flex-col gap-2 col-span-1 min-h-28 w-full shadow-2xl p-6 justify-center"
          :style="{ 'background-color': cardColors[4] }"
        >
          <p class="text-2xl">Số người truy cập 30 phút qua</p>
          <h5 class="text-[34px] font-bold">
            {{ formatNumber(report.data?.truy_cap_30p) || '0' }}
          </h5>
        </div>
      </div>
    </div>
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-4">
      <div
        class="flex flex-col col-span-1 p-4 border border-gray-300 shadow-2xl rounded-sm mb-4"
      >
        <h4 class="mb-4">Những trang được xem nhiều nhất</h4>
        <div v-if="options.chart_page?.rows.length">
          <Bar :options="options.chart_page"></Bar>
        </div>
        <div v-else class="flex items-center justify-center text-center h-full">
          Chưa có dữ liệu báo cáo
        </div>
      </div>
      <div
        class="col-span-1 p-4 border border-gray-300 shadow-2xl rounded-sm mb-4"
      >
        <h4 class="mb-4">Số lượt điền form</h4>
        <div>
          <Line :options="options?.chart_form"></Line>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import LayoutHeader from '@/components/LayoutHeader.vue'
import { ref, watch, inject, onMounted, onBeforeUnmount } from 'vue'
import { Breadcrumbs, createResource } from 'frappe-ui'
import FilterDashboard from '@/components/FilterDashboard.vue'
import Line from '@/components/Charts/Line/Line.vue'
import Bar from '@/components/Charts/Bar/Bar.vue'
import { errorMessage, formatNumber } from '@/utils'
import CardDashboard from '@/components/CardDashboard.vue'
const socket = inject('$socket')

const breadcrumbs = [{ label: 'Dashboard', route: { name: 'Dashboard' } }]
const msgError = ref()
const filterChange = ref(false)

const cardColors = ['#fcf2f3', '#f4e1e1', '#f3c9cc', '#f8a6ab', '#f8a6ab']
const timeRangeStart = ref('')
const timeRangeEnd = ref('')
const selectedCompare = ref()

const options = ref({
  chart_access: {
    rows: [],
    colors: ['#e98282', '#edaeae'],
    columns: [],
    data: [],
  },
  chart_page: {
    rows: [],
    colors: ['#e98282'],
    data: [],
  },
  chart_form: {
    columns: [],
    rows: [],
    colors: ['#e98282', '#edaeae'],
    data: [],
  },
})
const infoCompare = ref({})

const report = createResource({
  url: 'go1_cms.api.report.report_dashboard',
  method: 'GET',
  params: {},
  transform: (data) => {
    // trang xem nhieu nhat
    let chart_page = {
      ...options.value.chart_page,
      rows: data?.trang_xem_nhieu.rows,
      data: [data?.trang_xem_nhieu.data],
    }
    if (selectedCompare.value.value !== 'khong_so_sanh') {
      let rows = chart_page.rows
      let trang_xem_nhieu_truoc = data?.trang_xem_nhieu_truoc
      let trang_xem_nhieu_htai = data?.trang_xem_nhieu.data.map((el, idx) => {
        let ti_le = trang_xem_nhieu_truoc[rows[idx]]
          ? ((el.value - trang_xem_nhieu_truoc[rows[idx]]) /
              trang_xem_nhieu_truoc[rows[idx]]) *
            100
          : 0
        return {
          name: rows[idx],
          value: el.value,
          compare: ti_le,
        }
      })

      chart_page = { ...chart_page, data: [trang_xem_nhieu_htai] }
    }

    // luot truy cap trang
    let data_chart = []
    if (data?.rp_range_start) {
      data_chart.push(data?.rp_range_start?.luot_truy_cap.data)
    }
    if (data?.rp_range_end) {
      data_chart.push(data?.rp_range_end?.luot_truy_cap.data)
    }

    let chart_access = {
      ...options.value.chart_access,
      rows: data?.rp_range_start?.luot_truy_cap.rows,
      columns: data?.rp_range_start?.luot_truy_cap.columns,
      data: data_chart,
    }
    // luot dien form
    data_chart = []
    if (data?.rp_range_start) {
      data_chart.push(data?.rp_range_start?.luot_dien_form.data)
    }
    if (data?.rp_range_end) {
      data_chart.push(data?.rp_range_end?.luot_dien_form.data)
    }

    let chart_form = {
      ...options.value.chart_access,
      rows: data?.rp_range_start?.luot_dien_form.rows,
      columns: data?.rp_range_start?.luot_dien_form.columns,
      data: data_chart,
    }

    options.value = {
      ...options.value,
      chart_page: chart_page,
      chart_access: chart_access,
      chart_form: chart_form,
    }

    if (selectedCompare.value.value != 'khong_so_sanh') {
      let kht_so_nguoi_dung = data.rp_range_start.so_nguoi_dung
      let kht_so_truy_cap = data.rp_range_start.so_truy_cap
      let kht_thoi_gian_xem_tb = data.rp_range_start.thoi_gian_xem_tb
      let kt_so_nguoi_dung = data.rp_range_end.so_nguoi_dung
      let kt_so_truy_cap = data.rp_range_end.so_truy_cap
      let kt_thoi_gian_xem_tb = data.rp_range_end.thoi_gian_xem_tb

      let ti_le_nguoi_dung = kt_so_nguoi_dung
        ? ((kht_so_nguoi_dung - kt_so_nguoi_dung) / kt_so_nguoi_dung) * 100
        : 0
      let ti_le_truy_cap = kt_so_truy_cap
        ? ((kht_so_truy_cap - kt_so_truy_cap) / kt_so_truy_cap) * 100
        : 0
      let ti_le_thoi_gian_xem_tb = kt_thoi_gian_xem_tb
        ? ((kht_thoi_gian_xem_tb - kt_thoi_gian_xem_tb) / kt_thoi_gian_xem_tb) *
          100
        : 0

      infoCompare.value = {
        ti_le_nguoi_dung: ti_le_nguoi_dung,
        ti_le_truy_cap: ti_le_truy_cap,
        ti_le_thoi_gian_xem_tb: ti_le_thoi_gian_xem_tb,
      }
    }

    return data
  },
  onError: (err) => {
    if (err.messages && err.messages.length) {
      msgError.value = err.messages.join(', ')
      errorMessage('Có lỗi xảy ra', err.messages.join(', '))
    } else {
      errorMessage('Có lỗi xảy ra', err)
    }
  },
})

function realtimeChart() {
  report.update({
    params: {
      time_range_start: timeRangeStart.value,
      time_range_end: timeRangeEnd.value,
      type_compare: selectedCompare.value?.value || '',
    },
  })
  report.fetch()
}

watch(filterChange, () => {
  if (
    ['tuy_chon', 'so_sanh_ky_truoc'].includes(selectedCompare.value?.value) &&
    !timeRangeEnd.value
  ) {
    return
  }
  realtimeChart()
})

onMounted(() => {
  socket.on('dashboard_update', (data) => {
    report.reload()
  })
})

onBeforeUnmount(() => {
  socket.off('dashboard_update')
})
</script>
