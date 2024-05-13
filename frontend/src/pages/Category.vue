<template>
  <LayoutHeader>
    <template #left-header>
      <Breadcrumbs :items="breadcrumbs" />
    </template>
  </LayoutHeader>
  <div class="p-6 mt-12">
    <div class="border-b pb-2 mb-4 border-gray-300">
      <div class="mb-4 flex justify-between gap-4">
        <h2 class="mb-2 font-bold text-3xl">Quản lý danh mục</h2>
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
      </div>
      <div>
        <div class="grid grid-cols-1 lg:grid-cols-4 sm:grid-cols-2 gap-4">
          <FormControl
            :type="'text'"
            size="sm"
            variant="subtle"
            placeholder=""
            :disabled="false"
            label="Tiêu đề"
            v-model="inputNameWeb"
          />
        </div>
      </div>
    </div>
    <div class="pb-4">
      <PostsListView
        class="min-h-[250px] max-h-[80vh]"
        v-model:loading="loading"
        :rows="dataRows"
        :columns="dataColums"
        :options="{
          selectable: false,
          showTooltip: false,
          resizeColumn: true,
          emptyState: {
            title: 'Bạn chưa có danh mục nào',
            description: 'Hãy thêm một danh mục mới cho website của bạn',
            button: {
              label: 'Thêm danh mục',
              variant: 'solid',
              theme: 'blue',
              onClick: () => {
                router.push({
                  name: 'Category Create',
                })
              },
            },
          },
        }"
        @reFresh="
          () => {
            reFresh = !reFresh
          }
        "
      ></PostsListView>
    </div>
  </div>
</template>

<script setup>
import LayoutHeader from '@/components/LayoutHeader.vue'
import PostsListView from '@/components/ListViews/PostsListView.vue'
import { Breadcrumbs } from 'frappe-ui'
import { useRouter } from 'vue-router'
import { ref, watch } from 'vue'

const router = useRouter()
const breadcrumbs = [
  { label: 'Quản lý bài viết', route: { name: 'Posts' } },
  { label: 'Quản lý danh mục', route: { name: 'Category' } },
]
const reFresh = ref(true)
const dataRows = ref([])
const dataColums = ref([
  {
    label: 'STT',
    key: 'stt',
    width: '50px',
  },
  {
    label: 'Tiêu đề',
    key: 'name_web',
  },
  {
    label: 'Hành dộng',
    key: 'action',
  },
])
</script>
