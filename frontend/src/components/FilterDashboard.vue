<template>
  <div class="mb-3">
    <div class="flex gap-4 items-end flex-wrap">
      <div>
        <NestedPopover>
          <template #target="{ open }">
            <Button
              variant="outline"
              theme="gray"
              size="md"
              @click="
                () => {
                  let p = timeRangeStart.split(',')
                  p = [new Date(p[0]), new Date(p[1])]
                  timeRangeStartCurrent = p
                  msgError.rangeStart = ''
                  selectedPeriodCurrent = selectedPeriod
                }
              "
            >
              <div class="truncate">{{ labelPeriod }}</div>
              <template #suffix>
                <FeatherIcon
                  :name="open ? 'chevron-up' : 'chevron-down'"
                  class="h-4 text-gray-600"
                />
              </template>
            </Button>
          </template>
          <template #body="{ open, close }">
            <div
              class="my-2 space-y-1.5 divide-y rounded-lg border border-gray-100 bg-white p-1.5 shadow-xl"
            >
              <div class="p-2 grid grid-cols-2 gap-2">
                <div
                  v-for="btn in optionsPeriods"
                  class="w-full"
                  :class="btn.value != 'tuy_chon' ? 'col-span-1' : 'col-span-2'"
                >
                  <Button
                    variant="outline"
                    :theme="
                      selectedPeriodCurrent.value == btn.value ? 'blue' : 'gray'
                    "
                    class="w-full"
                    :label="btn.label"
                    @click="
                      () => {
                        selectedPeriodCurrent = { ...btn }
                        handleSelectPeriod(close, false)
                      }
                    "
                  ></Button>
                </div>
                <div class="col-span-2">
                  <VueDatePicker
                    v-model="timeRangeStartCurrent"
                    range
                    :enable-time-picker="false"
                    format="dd/MM/yyyy"
                    :disabled="selectedPeriodCurrent.value != 'tuy_chon'"
                  ></VueDatePicker>
                  <ErrorMessage class="mt-1" :message="msgError.rangeStart" />
                </div>
                <div
                  v-if="selectedPeriodCurrent.value == 'tuy_chon'"
                  class="col-span-2"
                >
                  <Button
                    class="w-full"
                    variant="solid"
                    theme="blue"
                    size="sm"
                    :label="__('Filter')"
                    @click="() => handleSelectPeriod(close)"
                  >
                  </Button>
                </div>
              </div>
            </div>
          </template>
        </NestedPopover>
      </div>
      <div>
        <NestedPopover>
          <template #target="{ open }">
            <Button
              variant="outline"
              theme="gray"
              size="md"
              @click="
                () => {
                  let p = timeRangeEnd.split(',')
                  p = [new Date(p[0]), new Date(p[1])]
                  timeRangeEndCurrent = p
                  msgError.rangeEnd = ''
                  selectedCompareCurrent = selectedCompare
                }
              "
            >
              <div class="flex flex-wrap gap-2 items-center">
                <div class="truncate">{{ labelCompare }}</div>
              </div>
              <template #suffix>
                <FeatherIcon
                  :name="open ? 'chevron-up' : 'chevron-down'"
                  class="h-4 text-gray-600"
                />
              </template>
            </Button>
          </template>
          <template #body="{ open, close }">
            <div
              class="my-2 space-y-1.5 divide-y rounded-lg border border-gray-100 bg-white p-1.5 shadow-xl"
            >
              <div class="p-2 grid grid-cols-2 gap-2">
                <div
                  v-for="btn in optionsCompare"
                  class="w-full"
                  :class="btn.value != 'tuy_chon' ? 'col-span-1' : 'col-span-2'"
                >
                  <Button
                    variant="outline"
                    :theme="
                      selectedCompareCurrent.value == btn.value
                        ? 'blue'
                        : 'gray'
                    "
                    class="w-full"
                    :label="btn.label"
                    @click="
                      () => {
                        selectedCompareCurrent = { ...btn }
                        handleSelectCompare(close, false)
                      }
                    "
                  ></Button>
                </div>
                <div
                  v-if="selectedCompareCurrent.value != 'khong_so_sanh'"
                  class="col-span-2"
                >
                  <div class="flex gap-2">
                    <VueDatePicker
                      v-model="timeRangeEndCurrent"
                      range
                      :enable-time-picker="false"
                      format="dd/MM/yyyy"
                      :disabled="selectedCompareCurrent.value != 'tuy_chon'"
                    ></VueDatePicker>
                  </div>
                  <ErrorMessage class="mt-1" :message="msgError.rangeEnd" />
                </div>
                <div
                  v-if="selectedCompareCurrent.value == 'tuy_chon'"
                  class="col-span-2"
                >
                  <Button
                    class="w-full"
                    variant="solid"
                    theme="blue"
                    size="sm"
                    label="Lọc"
                    @click="() => handleSelectCompare(close)"
                  >
                  </Button>
                </div>
              </div>
            </div>
          </template>
        </NestedPopover>
      </div>
    </div>
  </div>
</template>

<script setup>
import NestedPopover from '@/components/NestedPopover.vue'
import { getCurrentDateInVietnam, getDateMinusDays } from '@/utils'
import { ref, watch, onMounted } from 'vue'
import moment from 'moment'
import { useRoute, useRouter } from 'vue-router'
const route = useRoute()
const router = useRouter()

const filterChange = defineModel()
const timeRangeStart = defineModel('timeRangeStart')
const timeRangeEnd = defineModel('timeRangeEnd')
const timeRangeStartCurrent = ref()
const timeRangeEndCurrent = ref()
const emit = defineEmits(['update'])

const labelPeriod = ref('')
const labelCompare = ref('')
const msgError = ref({})

const selectedPeriod = ref({
  value: '7_ngay_qua',
  label: __('Last 7 days'),
})
const selectedPeriodCurrent = ref({
  value: '7_ngay_qua',
  label: __('Last 7 days'),
})
const optionsPeriods = [
  {
    value: 'hom_nay',
    label: __('Today'),
  },
  {
    value: 'hom_qua',
    label: __('Yesterday'),
  },
  {
    value: '7_ngay_qua',
    label: __('Last 7 days'),
  },
  {
    value: '30_ngay_qua',
    label: __('Last 30 days'),
  },
  {
    value: 'tuan_truoc',
    label: __('Last week'),
  },
  {
    value: 'tuan_nay',
    label: __('This week'),
  },
  {
    value: 'thang_truoc',
    label: __('Last month'),
  },
  {
    value: 'thang_nay',
    label: __('This month'),
  },
  {
    value: 'tuy_chon',
    label: __('Options'),
  },
]

const selectedCompare = ref({
  value: 'khong_so_sanh',
  label: __('No comparison'),
})
const selectedCompareCurrent = ref({
  value: 'khong_so_sanh',
  label: __('No comparison'),
})

const optionsCompare = [
  {
    value: 'khong_so_sanh',
    label: __('No comparison'),
  },
  {
    value: 'so_sanh_ky_truoc',
    label: __('Compare with previous period'),
  },
  {
    value: 'tuy_chon',
    label: __('Options'),
  },
]
function handleSetLabelCompare() {
  let str_time = ''
  switch (selectedCompare.value.value) {
    case 'khong_so_sanh':
      setLabelCompare(str_time)
      break
    case 'tuy_chon':
      if (timeRangeEndCurrent.value) {
        let p = timeRangeEndCurrent.value
        str_time = `${moment(p[0]).format('DD/MM/YYYY')} - ${moment(
          p[1],
        ).format('DD/MM/YYYY')}`
        setLabelCompare(str_time)
      }
      break
    case 'so_sanh_ky_truoc':
      changeValueTime()
      break
  }
}
function handleSelectCompare(close, allow_close = true) {
  if (
    selectedCompareCurrent.value.value == 'tuy_chon' &&
    !timeRangeEndCurrent.value
  ) {
    msgError.value.rangeEnd = __('Please select a date range')
    return
  }
  selectedCompare.value = { ...selectedCompareCurrent.value }
  handleSetLabelCompare()

  updateFilter()
  if (allow_close) {
    close()
  }
}

function handleSelectPeriod(close, allow_close = true) {
  if (
    selectedPeriodCurrent.value.value == 'tuy_chon' &&
    !timeRangeStartCurrent.value
  ) {
    msgError.value.rangeStart = __('Please select a date range')
    return
  }
  selectedPeriod.value = { ...selectedPeriodCurrent.value }
  changeValueTime()

  updateFilter()
  if (allow_close) {
    close()
  }
}

function updateFilter() {
  setQueryParams()
  emit('update', selectedCompare.value)
  filterChange.value = !filterChange.value
}

function setQueryParams() {
  let query = {
    selected_period: selectedPeriod.value.value,
    selected_compare: selectedCompare.value.value,
  }
  if (selectedPeriod.value.value == 'tuy_chon') {
    let p = timeRangeStartCurrent.value
    p = `${moment(p[0]).format('YYYY-MM-DD')},${moment(p[1]).format(
      'YYYY-MM-DD',
    )}`
    query.time_range_start = p
  }
  if (selectedCompare.value.value == 'tuy_chon') {
    let p = timeRangeEndCurrent.value
    p = `${moment(p[0]).format('YYYY-MM-DD')},${moment(p[1]).format(
      'YYYY-MM-DD',
    )}`
    query.time_range_end = p
  }

  router.push({
    path: route.path,
    query: query,
  })
}

function getQueryParams() {
  // period
  let default_period = { value: '7_ngay_qua', label: __('Last 7 days') }
  let period = optionsPeriods.find(
    (el) => el.value == route.query.selected_period,
  )

  selectedPeriod.value = period ? period : default_period
  selectedPeriodCurrent.value = period ? period : default_period

  if (period?.value == 'tuy_chon' && route.query.time_range_start) {
    let t = route.query.time_range_start.split(',')
    if (t.length == 2) {
      timeRangeStartCurrent.value = [new Date(t[0]), new Date(t[1])]
      let textLeft = `${moment(new Date(t[0])).format('DD/MM/YYYY')} - ${moment(
        new Date(t[1]),
      ).format('DD/MM/YYYY')}`
      setLablePeriod(textLeft)
    }
  }

  changeValueTime()

  // compare
  let default_compare = {
    value: 'khong_so_sanh',
    label: __('No comparison'),
  }
  let compare = optionsCompare.find(
    (el) => el.value == route.query.selected_compare,
  )

  selectedCompare.value = compare ? compare : default_compare
  selectedCompareCurrent.value = compare ? compare : default_compare

  if (compare?.value == 'tuy_chon' && route.query.time_range_end) {
    let t = route.query.time_range_end.split(',')
    if (t.length == 2) {
      timeRangeEnd.value = `${t[0]},${t[1]}`
      timeRangeEndCurrent.value = [new Date(t[0]), new Date(t[1])]
    }
  } else {
    let t = timeRangeEndCurrent.value
    if (t) {
      timeRangeEnd.value = `${moment(new Date(t[0])).format(
        'YYYY-MM-DD',
      )},${moment(new Date(t[1])).format('YYYY-MM-DD')}`
    }
  }

  handleSetLabelCompare()
}

function calculateLastWeek() {
  const startOfWeek = moment().startOf('isoWeek')
  const startOfLastWeek = startOfWeek.clone().subtract(1, 'week')
  const endOfLastWeek = startOfWeek.clone().subtract(1, 'day')

  var a = startOfLastWeek.format('YYYY-MM-DD')
  var b = endOfLastWeek.format('YYYY-MM-DD')
  return {
    from: a,
    to: b,
    numberOfDays: endOfLastWeek.diff(startOfLastWeek, 'days') + 1,
  }
}

function calculateThisWeek() {
  const startOfThisWeek = moment().startOf('isoWeek')
  const endOfThisWeek = moment()

  var a = startOfThisWeek.format('YYYY-MM-DD')
  return {
    from: a,
    to: endOfThisWeek.format('YYYY-MM-DD'),
    numberOfDays: endOfThisWeek.diff(startOfThisWeek, 'days') + 1,
  }
}

function calculateLastMonth() {
  const startOfLastMonth = moment().subtract(1, 'month').startOf('month')
  const endOfLastMonth = moment().subtract(1, 'month').endOf('month')

  var a = startOfLastMonth.format('YYYY-MM-DD')
  var b = endOfLastMonth.format('YYYY-MM-DD')
  var c = endOfLastMonth.diff(startOfLastMonth, 'days') + 1
  return {
    from: a,
    to: b,
    numberOfDays: c,
  }
}

function calculateDaysFromStartOfMonth() {
  const startOfThisMonth = moment().startOf('month')
  const today = moment()

  var a = startOfThisMonth.format('YYYY-MM-DD')
  var b = today.format('YYYY-MM-DD')
  var c = today.diff(startOfThisMonth, 'days') + 1
  return {
    from: a,
    to: b,
    numberOfDays: c,
  }
}

function setLablePeriod(text) {
  labelPeriod.value = `${selectedPeriod.value.label} (${text})`
}
function setLabelCompare(str_time) {
  let val = selectedCompare.value.value
  if (val == 'so_sanh_ky_truoc') {
    labelCompare.value = `${__('Compared to')}: ${str_time}`
  } else if (val == 'tuy_chon') {
    labelCompare.value = `Options (${str_time})`
  } else {
    labelCompare.value = __('No comparison')
  }
}

function changeFilter(d_time) {
  let fromDate = d_time?.from
  let toDate = d_time?.to
  let fromDate1 = getDateMinusDays(fromDate, d_time.numberOfDays)
  let toDate1 = getDateMinusDays(fromDate, 1)
  let textLeft = `${moment(new Date(fromDate)).format('DD/MM/YYYY')} - ${moment(
    new Date(toDate),
  ).format('DD/MM/YYYY')}`
  let textRight = `${moment(new Date(fromDate1)).format(
    'DD/MM/YYYY',
  )} - ${moment(new Date(toDate1)).format('DD/MM/YYYY')}`
  setLabelText(textLeft, textRight)
  setValueTime(fromDate, toDate, fromDate1, toDate1)
}

function setLabelText(textLeft, textRight) {
  setLablePeriod(textLeft)
  setLabelCompare(textRight)
}

//
function setValueTime(fromDate, toDate, fromDate1, toDate1) {
  timeRangeStartCurrent.value = [new Date(fromDate), new Date(toDate)]
  timeRangeEndCurrent.value = [new Date(fromDate1), new Date(toDate1)]
  timeRangeStart.value = `${fromDate},${toDate}`
  timeRangeEnd.value = `${fromDate1},${toDate1}`
}

function changeValueTime() {
  let val = selectedPeriod.value.value
  let today = getCurrentDateInVietnam()
  let fromDate = today
  let toDate = today
  let fromDate1 = getDateMinusDays(fromDate, 1)
  let toDate1 = getDateMinusDays(fromDate, 1)
  let textLeft = ''
  let textRight = ''
  switch (val) {
    case 'hom_nay':
      textLeft = `${moment(new Date(toDate)).format('DD/MM/YYYY')}`
      textRight = `${moment(new Date(toDate1)).format('DD/MM/YYYY')}`
      setLabelText(textLeft, textRight)
      setValueTime(fromDate, toDate, fromDate1, toDate1)
      break
    case 'hom_qua':
      fromDate = getDateMinusDays(today, 1)
      toDate = getDateMinusDays(today, 1)
      fromDate1 = getDateMinusDays(fromDate, 1)
      toDate1 = getDateMinusDays(fromDate, 1)
      textLeft = `${moment(new Date(toDate)).format('DD/MM/YYYY')}`
      textRight = `${moment(new Date(toDate1)).format('DD/MM/YYYY')}`
      setLabelText(textLeft, textRight)
      setValueTime(fromDate, toDate, fromDate1, toDate1)
      break
    case '7_ngay_qua':
      fromDate = getDateMinusDays(today, 6)
      toDate = today
      fromDate1 = getDateMinusDays(fromDate, 7)
      toDate1 = getDateMinusDays(fromDate, 1)
      textLeft = `${moment(new Date(fromDate)).format('DD/MM/YYYY')} - ${moment(
        new Date(toDate),
      ).format('DD/MM/YYYY')}`
      textRight = `${moment(new Date(fromDate1)).format(
        'DD/MM/YYYY',
      )} - ${moment(new Date(toDate1)).format('DD/MM/YYYY')}`
      setLabelText(textLeft, textRight)
      setValueTime(fromDate, toDate, fromDate1, toDate1)
      break
    case '30_ngay_qua':
      fromDate = getDateMinusDays(today, 29)
      toDate = today
      fromDate1 = getDateMinusDays(fromDate, 30)
      toDate1 = getDateMinusDays(fromDate, 1)
      textLeft = `${moment(new Date(fromDate)).format('DD/MM/YYYY')} - ${moment(
        new Date(toDate),
      ).format('DD/MM/YYYY')}`
      textRight = `${moment(new Date(fromDate1)).format(
        'DD/MM/YYYY',
      )} - ${moment(new Date(toDate1)).format('DD/MM/YYYY')}`
      setLabelText(textLeft, textRight)
      setValueTime(fromDate, toDate, fromDate1, toDate1)
      break
    case 'tuan_truoc':
      var tuan_truoc = calculateLastWeek()
      changeFilter(tuan_truoc)
      break
    case 'tuan_nay':
      var tuan_nay = calculateThisWeek()
      changeFilter(tuan_nay)
      break
    case 'thang_truoc':
      var thang_truoc = calculateLastMonth()
      changeFilter(thang_truoc)
      break
    case 'thang_nay':
      var thang_nay = calculateDaysFromStartOfMonth()
      changeFilter(thang_nay)
      break
    case 'tuy_chon':
      if (
        selectedPeriod.value.value == 'tuy_chon' &&
        timeRangeStartCurrent.value
      ) {
        let p = timeRangeStartCurrent.value
        p = [
          moment(p[0]).format('YYYY-MM-DD'),
          moment(p[1]).format('YYYY-MM-DD'),
        ]
        var tuy_chon = calculateDaysBetweenDates(p[0], p[1])
        changeFilter(tuy_chon)
      }
      break
    default:
      break
  }
}

onMounted(() => {
  handleLoadFirst()
})

watch(route, (val) => {
  handleLoadFirst()
})

function handleLoadFirst() {
  getQueryParams()
  emit('update', selectedCompare.value)
  filterChange.value = !filterChange.value
}

function calculateDaysBetweenDates(strStart, strEnd) {
  const startDate = moment(strStart)
  const endDate = moment(strEnd)

  var a = startDate.format('YYYY-MM-DD')
  var b = endDate.format('YYYY-MM-DD')
  var c = endDate.diff(startDate, 'days') + 1
  return {
    from: a,
    to: b,
    numberOfDays: c,
  }
}

watch(timeRangeStartCurrent, (val) => {
  if (val) {
    let str_time = `${moment(val[0]).format('YYYY-MM-DD')},${moment(
      val[1],
    ).format('YYYY-MM-DD')}`
    timeRangeStart.value = str_time
  } else {
    msgError.value.rangeStart = __('Please select a date range')
  }
})

watch(timeRangeEndCurrent, (val) => {
  if (val) {
    let str_time = `${moment(val[0]).format('YYYY-MM-DD')},${moment(
      val[1],
    ).format('YYYY-MM-DD')}`
    timeRangeEnd.value = str_time
  } else {
    msgError.value.rangeEnd = __('Please select a date range')
  }
})
</script>
