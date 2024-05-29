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
          label="Thêm mới"
          iconLeft="plus-circle"
          route="/category/create"
        >
        </Button>
      </div>
    </template>
  </LayoutHeader>
  <div class="flex-1 flex flex-col h-full overflow-auto p-6 pb-4">
    <ViewControls
      ref="viewControls"
      v-model="category"
      v-model:loadMore="loadMore"
      v-model:resizeColumn="triggerResize"
      v-model:updatedPageCount="updatedPageCount"
      :options="{
        hideColumnsButton: true,
      }"
      doctype="Mbw Blog Category"
    />
    <CategoryListView
      v-if="category.data && rows.length"
      v-model="category.data.page_length_count"
      v-model:list="category"
      :rows="rows"
      :columns="columns"
      :options="{
        rowCount: category.data.row_count,
        totalCount: category.data.total_count,
        selectable: false,
        showTooltip: false,
        resizeColumn: true,
      }"
      @loadMore="() => loadMore++"
      @columnWidthUpdated="() => triggerResize++"
      @updatePageCount="(count) => (updatedPageCount = count)"
      @applyFilter="(data) => viewControls.applyFilter(data)"
    ></CategoryListView>
    <div
      v-else-if="category.data"
      class="flex flex-1 items-center justify-center"
    >
      <div
        class="flex flex-col items-center gap-3 text-xl font-medium text-gray-500"
      >
        <PostIcon class="h-10 w-10" />
        <span>{{ __('No Category Found') }}</span>
        <Button :label="__('Thêm mới')" route="/category/create">
          <template #prefix><FeatherIcon name="plus" class="h-4" /></template>
        </Button>
      </div>
    </div>
  </div>
</template>

<script setup>
import LayoutHeader from '@/components/LayoutHeader.vue'
import PostIcon from '@/components/Icons/PostIcon.vue'
import CategoryListView from '@/components/ListViews/CategoryListView.vue'
import ViewControls from '@/components/ViewControls.vue'
import { Breadcrumbs } from 'frappe-ui'
import { ref, computed } from 'vue'

const breadcrumbs = [
  { label: 'Quản lý bài viết', route: { name: 'Posts' } },
  { label: 'Quản lý danh mục', route: { name: 'Category' } },
]

// leads data is loaded in the ViewControls component
const category = ref({})
const loadMore = ref(1)
const triggerResize = ref(1)
const updatedPageCount = ref(20)
const viewControls = ref(null)

// Columns
const columns = computed(() => {
  if (!category.value?.data?.columns) return []

  let _columns = category.value?.data?.columns
  if (!_columns.find((el) => el.key == 'action_button')) {
    _columns.push({ label: __('Action'), key: 'action_button' })
  }
  return _columns
})

// Rows
const rows = computed(() => {
  if (!category.value?.data?.data) return []
  return category.value?.data.data.map((cat) => {
    let _rows = {}
    category.value?.data.rows.forEach((row) => {
      _rows[row] = cat[row]
    })
    _rows['action_button'] = { ...cat }
    return _rows
  })
})
</script>
