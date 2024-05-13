<template>
  <LayoutHeader>
    <template #left-header>
      <Breadcrumbs :items="breadcrumbs" />
    </template>
  </LayoutHeader>
  <div class="p-6 mt-12">
    <div class="border-b pb-2 mb-4 border-gray-300">
      <div>
        <h2 class="font-bold text-3xl">
          {{ page_detail.data?.doc_item.name_page }}
        </h2>
      </div>
    </div>
    <div class="p-4 border border-gray-300 rounded-sm mb-4">
      <div class="p-2">
        <div>
          <div class="mb-4">
            <h2 class="font-bold text-xl">SEO</h2>
          </div>
          <div class="grid lg:grid-cols-2 gap-4">
            <div class="flex flex-col gap-4">
              <FormControl
                :type="'text'"
                size="md"
                variant="subtle"
                placeholder="Nhập tiêu đề"
                label="Tiêu đề"
                v-model="inputValue"
              />
              <FormControl
                :type="'textarea'"
                size="md"
                variant="subtle"
                placeholder="Nhập từ khóa"
                label="Thẻ từ khóa"
                v-model="inputValue"
                rows="4"
              />
            </div>
            <div class="flex flex-col gap-4">
              <FormControl
                :type="'textarea'"
                size="md"
                variant="subtle"
                placeholder="Nhập mô tả"
                label="Thẻ mô tả"
                v-model="inputValue"
                rows="9"
              />
            </div>
          </div>
        </div>
        <div class="flex mt-4 border-t py-2 rounded-sm gap-2 justify-end">
          <Button
            :variant="'solid'"
            theme="blue"
            size="md"
            label="Lưu"
          ></Button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import LayoutHeader from '@/components/LayoutHeader.vue'
import { Breadcrumbs, FormControl, createResource } from 'frappe-ui'
import { useRouter, useRoute } from 'vue-router'
import { ref, computed, onMounted, watch } from 'vue'

const route = useRoute()

// get detail
const page_detail = createResource({
  url: 'go1_cms.api.client_website.get_page_detail',
  method: 'GET',
  params: { name: route.query.view },
  auto: true,
})

watch(route, (val, oldVal) => {
  page_detail.update({
    params: { name: route.query.view },
  })
  page_detail.reload()
})

const breadcrumbs = computed(() => {
  let items = []
  items.push({
    label: page_detail.data?.doc_item.name_page,
    route: {
      name: 'Page',
      query: { view: route.query.view },
    },
  })
  return items
})
</script>
