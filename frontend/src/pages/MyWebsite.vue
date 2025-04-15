<template>
  <LayoutHeader>
    <template #left-header>
      <Breadcrumbs :items="breadcrumbs" />
    </template>
    <template #right-header>
      <div>
        <Button
          :variant="'solid'"
          theme="blue"
          size="sm"
          :label="__('Add New')"
          iconLeft="plus-circle"
          route="/interface-repository"
        >
        </Button>
      </div>
    </template>
  </LayoutHeader>
  <div class="flex-1 flex flex-col h-full overflow-auto p-6 pt-2 pb-4">
    <div class="pt-4">
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
          <Button :label="__('Add New')" route="/interface-repository">
            <template #prefix><FeatherIcon name="plus" class="h-4" /></template>
          </Button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import MyWebsitesListView from '@/components/ListViews/MyWebsitesListView.vue'
import MyWebsiteIcon from '@/components/Icons/MyWebsiteIcon.vue'
import LayoutHeader from '@/components/LayoutHeader.vue'
import { Breadcrumbs, createResource } from 'frappe-ui'
import { computed } from 'vue'

const breadcrumbs = [
  { label: 'Website của tôi', route: { name: 'My Website' } },
]

const clientWebsite = createResource({
  url: 'go1_cms.api.client_website.get_client_websites',
  auto: true,
  onSuccess(data) {
    return data
  },
})

// Columns
const columns = computed(() => {
  if (!clientWebsite?.data?.columns) return []

  let _columns = clientWebsite?.data?.columns
  if (!_columns.find((el) => el.key == 'action_button')) {
    _columns.push({ label: __('Action'), key: 'action_button' })
  }
  return _columns
})

// Rows
const rows = computed(() => {
  if (!clientWebsite?.data?.data) return []
  return clientWebsite?.data.data.map((cat) => {
    let _rows = {}
    clientWebsite?.data.rows.forEach((row) => {
      _rows[row] = cat[row]
    })
    _rows['action_button'] = { ...cat }
    return _rows
  })
})
</script>
