<template>
  <LayoutHeader>
    <template #left-header>
      <Breadcrumbs :items="breadcrumbs" />
    </template>
  </LayoutHeader>
  <div class="p-6">
    <MyWebsitesListView
      :rows="dataRows"
      :columns="dataColums"
      :options="{
        selectable: false,
        showTooltip: false,
        resizeColumn: true,
      }"
    />
  </div>
</template>

<script setup>
import MyWebsitesListView from '@/components/ListViews/MyWebsitesListView.vue'
import LayoutHeader from '@/components/LayoutHeader.vue'
import { Breadcrumbs, createResource } from 'frappe-ui'
import { createToast, errorMessage } from '@/utils'
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
const router = useRouter()

const breadcrumbs = [{ label: 'My Website', route: { name: 'My Website' } }]

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
    label: 'Trang thái',
    key: 'status_web',
  },
  {
    label: 'Phát hành',
    key: 'published',
  },
  {
    label: 'Chỉnh sửa',
    key: 'edit',
  },
  {
    label: 'Hành dộng',
    key: 'action',
  },
])

createResource({
  url: 'go1_cms.api.client_website.get_client_websites',
  auto: true,
  onSuccess: (data) => {
    data.forEach((el, idx) => {
      dataRows.value.push({
        stt: idx + 1,
        name_web: el.name_web,
        status_web: el.status_web,
        published: el.published,
        edit: el.edit,
        action: null,
      })
    })
    return data
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
</script>
