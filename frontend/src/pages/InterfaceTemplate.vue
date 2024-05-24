<template>
  <LayoutHeader>
    <template #left-header>
      <Breadcrumbs :items="breadcrumbs" />
    </template>
  </LayoutHeader>
  <div class="p-6 mt-12">
    <div class="border-b mb-4 pb-2 border-gray-300">
      <div class="flex flex-wrap justify-between items-center gap-2">
        <h2 class="font-bold text-3xl">{{ template.data?.name }}</h2>
        <Button
          :variant="'subtle'"
          theme="gray"
          size="sm"
          label="Chọn giao diện này"
          @click="addWebTemplate"
        >
        </Button>
      </div>
    </div>
    <div class="pb-4" v-html="template.data?.content"></div>
  </div>
</template>

<script setup>
const props = defineProps({
  interfaceId: {
    type: String,
    required: true,
  },
})

import LayoutHeader from '@/components/LayoutHeader.vue'
import { Breadcrumbs, createResource, call } from 'frappe-ui'
import { ref, computed, onMounted } from 'vue'
import { createToast, errorMessage } from '@/utils'
import { useRouter } from 'vue-router'
const router = useRouter()
import { globalStore } from '@/stores/global'
const { changeLoadingValue } = globalStore()

// get detail
const template = createResource({
  url: 'go1_cms.api.mbw_website_template.get_web_template',
  method: 'GET',
  params: { name: props.interfaceId },
  cache: ['template', props.interfaceId],
  auto: true,
})

// add web template
async function addWebTemplate() {
  changeLoadingValue(true, 'Đang tải giao diện...')
  try {
    await call('go1_cms.api.mbw_website_template.add_web_template', {
      name: props.interfaceId,
    }).then((d) => {
      if (d) {
        createToast({
          title: 'Tải giao diện thành công',
          icon: 'check',
          iconClasses: 'text-green-600',
        })
        changeLoadingValue(false)
        if (d.template_edit) {
          router.push({ name: 'My Website' })
        } else {
          window.location.href = '/cms/my-website'
        }
      }
    })
  } catch (err) {
    changeLoadingValue(false)
    if (err.messages && err.messages.length) {
      errorMessage('Có lỗi xảy ra', err.messages[0])
    }
  }
}

const breadcrumbs = computed(() => {
  let items = [
    { label: 'Kho giao diện', route: { name: 'Interface Repository' } },
  ]
  items.push({
    label: template.data?.name,
    route: {
      name: 'Interface Template',
      params: { interfaceId: props.interfaceId },
    },
  })
  return items
})
</script>
