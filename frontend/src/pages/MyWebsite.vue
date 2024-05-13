<template>
  <LayoutHeader>
    <template #left-header>
      <Breadcrumbs :items="breadcrumbs" />
    </template>
  </LayoutHeader>
  <div class="p-6 mt-12">
    <div class="border-b pb-2 mb-4 border-gray-300">
      <div class="mb-4">
        <h2 class="mb-2 font-bold text-3xl">Website của tôi</h2>
      </div>
      <div>
        <div class="grid grid-cols-1 lg:grid-cols-4 sm:grid-cols-2 gap-4">
          <FormControl
            :type="'text'"
            size="sm"
            variant="subtle"
            placeholder=""
            :disabled="false"
            label="Tên website"
            v-model="inputNameWeb"
          />
          <FormControl
            type="select"
            :options="[
              {
                label: 'Tất cả',
                value: 'all',
              },
              {
                label: 'Bản chính',
                value: 'Bản chính',
              },
              {
                label: 'Bản nháp',
                value: 'Bản nháp',
              },
            ]"
            size="sm"
            variant="subtle"
            :disabled="false"
            label="Loại"
            v-model="selectStatus"
          />
        </div>
      </div>
    </div>
    <div class="pb-4">
      <MyWebsitesListView
        class="min-h-[250px] max-h-[80vh]"
        v-model:loading="loading"
        :rows="dataRows"
        :columns="dataColums"
        :options="{
          selectable: false,
          showTooltip: false,
          resizeColumn: true,
          emptyState: {
            title: 'Bạn chưa có website nào',
            description: 'Chọn một mẫu website từ kho giao diện để bắt đầu',
            button: {
              label: 'Đến kho giao diện',
              variant: 'solid',
              theme: 'blue',
              onClick: () => {
                router.push({
                  name: 'Interface Repository',
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
      />
    </div>
  </div>
</template>

<script setup>
import MyWebsitesListView from '@/components/ListViews/MyWebsitesListView.vue'
import LayoutHeader from '@/components/LayoutHeader.vue'
import { Breadcrumbs, createResource } from 'frappe-ui'
import { createToast, errorMessage } from '@/utils'
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
const router = useRouter()

const breadcrumbs = [
  { label: 'Website của tôi', route: { name: 'My Website' } },
]

const loading = ref(true)
const reFresh = ref(true)
const dataRows = ref([])
const dataColums = ref([
  {
    label: 'STT',
    key: 'stt',
    width: '50px',
  },
  {
    label: 'Tên website',
    key: 'name_web',
  },
  {
    label: 'Loại',
    key: 'status_web',
  },
  {
    label: 'Trang thái',
    key: 'published',
  },
  {
    label: 'Website chỉnh sửa',
    key: 'edit',
  },
  {
    label: 'Hành dộng',
    key: 'action',
  },
])
const selectStatus = ref('all')
const inputNameWeb = ref()

const client_websites = createResource({
  url: 'go1_cms.api.client_website.get_client_websites',
  method: 'GET',
  auto: true,
  onSuccess: (data) => {
    let dtRows = []
    data.forEach((el, idx) => {
      dtRows.push({
        stt: idx + 1,
        name_web: el.name_web,
        status_web: el.status_web,
        published: el.published,
        edit: el.edit,
        action: {
          id: el.name,
          name_web: el.name_web,
          route_web: el.route_web,
          published: el.published,
          status_web: el.status_web,
          edit: el.edit,
        },
      })
    })
    dataRows.value = dtRows
    loading.value = false
  },
  onError: (err) => {
    createToast({
      title: 'Có lỗi xảy ra',
      text: err.messages?.[0],
      icon: 'x',
      iconClasses: 'text-red-600',
    })
  },
})

watch(reFresh, (val, old_value) => {
  client_websites.reload()
})
</script>
