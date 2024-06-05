<template>
  <LayoutHeader>
    <template #left-header>
      <Breadcrumbs :items="breadcrumbs" />
    </template>
    <template #right-header>
      <Button
        :variant="'solid'"
        theme="blue"
        size="sm"
        label="Thêm mới"
        iconLeft="plus-circle"
        route="/posts/create"
      >
      </Button>
    </template>
  </LayoutHeader>
  <div class="flex-1 flex flex-col h-full overflow-auto p-6 pb-4">
    <div>
      <Button
        :variant="'ghost'"
        theme="gray"
        size="sm"
        label="Quản lý danh mục"
        route="/category"
        iconLeft="edit"
      >
      </Button>
    </div>
    <ViewControls
      ref="viewControls"
      v-model="post"
      v-model:loadMore="loadMore"
      v-model:resizeColumn="triggerResize"
      v-model:updatedPageCount="updatedPageCount"
      :options="{
        hideColumnsButton: true,
      }"
      doctype="Mbw Blog Post"
    />
    <PostsListView
      v-if="post.data && rows.length"
      v-model="post.data.page_length_count"
      v-model:list="post"
      :rows="rows"
      :columns="columns"
      :options="{
        rowCount: post.data.row_count,
        totalCount: post.data.total_count,
        selectable: false,
        showTooltip: false,
        resizeColumn: true,
      }"
      @loadMore="() => loadMore++"
      @columnWidthUpdated="() => triggerResize++"
      @updatePageCount="(count) => (updatedPageCount = count)"
      @applyFilter="(data) => viewControls.applyFilter(data)"
    ></PostsListView>
    <div v-else-if="post.data" class="flex flex-1 items-center justify-center">
      <div
        class="flex flex-col items-center gap-3 text-xl font-medium text-gray-500"
      >
        <PostIcon class="h-10 w-10" />
        <span>{{ __('No Post Found') }}</span>
        <Button :label="__('Create')" route="/posts/create">
          <template #prefix><FeatherIcon name="plus" class="h-4" /></template>
        </Button>
      </div>
    </div>
  </div>
</template>

<script setup>
import LayoutHeader from '@/components/LayoutHeader.vue'
import PostIcon from '@/components/Icons/PostIcon.vue'
import PostsListView from '@/components/ListViews/PostsListView.vue'
import ViewControls from '@/components/ViewControls.vue'
import { Breadcrumbs } from 'frappe-ui'
import { ref, computed } from 'vue'

const breadcrumbs = [{ label: 'Quản lý bài viết', route: { name: 'Posts' } }]

// leads data is loaded in the ViewControls component
const post = ref({})
const loadMore = ref(1)
const triggerResize = ref(1)
const updatedPageCount = ref(20)
const viewControls = ref(null)

// Columns
const columns = computed(() => {
  if (!post.value?.data?.columns) return []

  let _columns = post.value?.data?.columns
  if (!_columns.find((el) => el.key == 'action_button')) {
    _columns.push({ label: __('Action'), key: 'action_button' })
  }
  return _columns
})

// Rows
const rows = computed(() => {
  if (!post.value?.data?.data) return []
  return post.value?.data.data.map((cat) => {
    let _rows = {}
    post.value?.data.rows.forEach((row) => {
      _rows[row] = cat[row]
    })
    _rows['action_button'] = { ...cat }
    return _rows
  })
})
</script>
