<template>
  <LayoutHeader>
    <template #left-header>
      <Breadcrumbs :items="breadcrumbs" />
    </template>
  </LayoutHeader>
  <div class="flex-1 flex flex-col h-full overflow-auto p-6 pb-4 mt-12">
    <div class="border-b pb-2 mb-4 border-gray-300">
      <div class="flex justify-between gap-4">
        <h2 class="mb-2 font-bold text-3xl">Website của tôi</h2>
        <div>
          <Button
            :variant="'solid'"
            theme="blue"
            size="sm"
            label="Thêm mới"
            iconLeft="plus-circle"
            route="/interface-repository"
          >
          </Button>
        </div>
      </div>
    </div>
    <ViewControls
      ref="viewControls"
      v-model="clientWebsite"
      v-model:loadMore="loadMore"
      v-model:resizeColumn="triggerResize"
      v-model:updatedPageCount="updatedPageCount"
      :options="{
        hideColumnsButton: true,
      }"
      doctype="MBW Client Website"
    />
    <MyWebsitesListView
      v-if="clientWebsite.data && rows.length"
      v-model="clientWebsite.data.page_length_count"
      v-model:list="clientWebsite"
      :rows="rows"
      :columns="columns"
      :options="{
        rowCount: clientWebsite.data.row_count,
        totalCount: clientWebsite.data.total_count,
        selectable: false,
        showTooltip: false,
        resizeColumn: true,
      }"
      @loadMore="() => loadMore++"
      @columnWidthUpdated="() => triggerResize++"
      @updatePageCount="(count) => (updatedPageCount = count)"
      @applyFilter="(data) => viewControls.applyFilter(data)"
    />
    <div
      v-else-if="clientWebsite.data"
      class="flex flex-1 items-center justify-center"
    >
      <div
        class="flex flex-col items-center gap-3 text-xl font-medium text-gray-500"
      >
        <MyWebsiteIcon class="h-10 w-10" />
        <span>{{
          __('Chọn một mẫu website từ kho giao diện để bắt đầu')
        }}</span>
        <Button :label="__('Thêm mới')" route="/interface-repository">
          <template #prefix><FeatherIcon name="plus" class="h-4" /></template>
        </Button>
      </div>
    </div>
  </div>
</template>

<script setup>
import ViewControls from '@/components/ViewControls.vue'
import MyWebsitesListView from '@/components/ListViews/MyWebsitesListView.vue'
import MyWebsiteIcon from '@/components/Icons/MyWebsiteIcon.vue'
import LayoutHeader from '@/components/LayoutHeader.vue'
import { Breadcrumbs } from 'frappe-ui'
import { ref, computed } from 'vue'

const breadcrumbs = [
  { label: 'Website của tôi', route: { name: 'My Website' } },
]

// leads data is loaded in the ViewControls component
const clientWebsite = ref({})
const loadMore = ref(1)
const triggerResize = ref(1)
const updatedPageCount = ref(20)
const viewControls = ref(null)

// Columns
const columns = computed(() => {
  if (!clientWebsite.value?.data?.columns) return []

  let _columns = clientWebsite.value?.data?.columns
  if (!_columns.find((el) => el.key == 'action_button')) {
    _columns.push({ label: __('Action'), key: 'action_button' })
  }
  return _columns
})

// Rows
const rows = computed(() => {
  if (!clientWebsite.value?.data?.data) return []
  return clientWebsite.value?.data.data.map((cat) => {
    let _rows = {}
    clientWebsite.value?.data.rows.forEach((row) => {
      _rows[row] = cat[row]
    })
    _rows['action_button'] = { ...cat }
    return _rows
  })
})
</script>
