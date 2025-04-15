<template>
  <LayoutHeader>
    <template #left-header>
      <Breadcrumbs :items="breadcrumbs" />
    </template>
    <template #right-header></template>
  </LayoutHeader>
  <div class="flex-1 flex flex-col h-full overflow-auto p-6 pt-2 pb-4">
    <ViewControls
      ref="viewControls"
      v-model="forms"
      v-model:loadMore="loadMore"
      v-model:resizeColumn="triggerResize"
      v-model:updatedPageCount="updatedPageCount"
      :options="{
        hideColumnsButton: true,
      }"
      doctype="MBW Form"
    />
    <FormsListView
      v-if="forms.data && rows.length"
      v-model="forms.data.page_length_count"
      v-model:list="forms"
      :rows="rows"
      :columns="columns"
      :options="{
        rowCount: forms.data.row_count,
        totalCount: forms.data.total_count,
        selectable: false,
        showTooltip: false,
        resizeColumn: true,
      }"
      @loadMore="() => loadMore++"
      @columnWidthUpdated="() => triggerResize++"
      @updatePageCount="(count) => (updatedPageCount = count)"
      @applyFilter="(data) => viewControls.applyFilter(data)"
    ></FormsListView>
    <div v-else-if="forms.data" class="flex flex-1 items-center justify-center">
      <div
        class="flex flex-col items-center gap-3 text-xl font-medium text-gray-500"
      >
        <PostIcon class="h-10 w-10" />
        <span>{{ __('No form available yet') }}</span>
      </div>
    </div>
  </div>
</template>

<script setup>
import LayoutHeader from '@/components/LayoutHeader.vue'
import PostIcon from '@/components/Icons/PostIcon.vue'
import FormsListView from '@/components/ListViews/FormsListView.vue'
import ViewControls from '@/components/ViewControls.vue'
import { Breadcrumbs } from 'frappe-ui'
import { ref, computed } from 'vue'

const breadcrumbs = [{ label: __('Form management'), route: { name: 'Forms' } }]

// leads data is loaded in the ViewControls component
const forms = ref({})
const loadMore = ref(1)
const triggerResize = ref(1)
const updatedPageCount = ref(20)
const viewControls = ref(null)

// Columns
const columns = computed(() => {
  if (!forms.value?.data?.columns) return []

  let _columns = forms.value?.data?.columns
  if (!_columns.find((el) => el.key == 'action_button')) {
    _columns.push({ label: __('Action'), key: 'action_button' })
  }
  return _columns
})

// Rows
const rows = computed(() => {
  if (!forms.value?.data?.data) return []
  return forms.value?.data.data.map((cat) => {
    let _rows = {}
    forms.value?.data.rows.forEach((row) => {
      _rows[row] = cat[row]
    })
    _rows['action_button'] = { ...cat }
    return _rows
  })
})
</script>
