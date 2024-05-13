<template>
  <LayoutHeader>
    <template #left-header>
      <Breadcrumbs :items="breadcrumbs" />
    </template>
  </LayoutHeader>
  <div class="p-6 mt-12">
    <div class="border-b pb-2 mb-4 border-gray-300">
      <div class="mb-4">
        <h2 class="mb-2 font-bold text-3xl">Quản lý bài viết</h2>
      </div>
      <div class="flex items-center gap-2 mb-4 justify-between">
        <Button
          :variant="'ghost'"
          theme="gray"
          size="sm"
          label="Quản lý danh mục"
          route="/category"
          iconLeft="edit"
        >
        </Button>
        <Button
          :variant="'solid'"
          theme="blue"
          size="sm"
          label="Thêm mới"
          iconLeft="plus-circle"
          route="/posts/create"
        >
        </Button>
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
          <FormControl
            type="select"
            :options="[
              {
                label: 'Tất cả',
                value: 'all',
              },
            ]"
            size="sm"
            variant="subtle"
            :disabled="false"
            label="Danh mục"
            v-model="selectStatus"
          />
          <FormControl
            type="select"
            :options="[
              {
                label: 'Tất cả',
                value: 'all',
              },
              {
                label: 'Hiển thị',
                value: 'Bản chính',
              },
              {
                label: 'Ẩn',
                value: 'Bản nháp',
              },
            ]"
            size="sm"
            variant="subtle"
            :disabled="false"
            label="Trạng thái"
            v-model="selectStatus"
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
            title: 'Bạn chưa có bài viết nào',
            description: 'Hãy thêm một bài viết mới cho website của bạn',
            button: {
              label: 'Thêm bài viết',
              variant: 'solid',
              theme: 'blue',
              onClick: () => {
                router.push({
                  name: 'Posts Create',
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
const breadcrumbs = [{ label: 'Quản lý bài viết', route: { name: 'Posts' } }]
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
    label: 'Danh mục',
    key: 'status_web',
  },
  {
    label: 'Trạng thái',
    key: 'published',
  },
  {
    label: 'Ngày đăng',
    key: 'edit',
  },
  {
    label: 'Hành dộng',
    key: 'action',
  },
])
</script>
