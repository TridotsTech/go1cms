<template>
  <LayoutHeader>
    <template #left-header>
      <Breadcrumbs :items="breadcrumbs" />
    </template>
  </LayoutHeader>
  <div class="p-6">
    <div class="border-b border-gray-300 pb-5">
      <div class="grid grid-cols-1 lg:grid-cols-4 sm:grid-cols-2">
        <FormControl
          type="select"
          :options="[
            {
              label: 'Tất cả',
              value: 'Tất cả',
            },
            {
              label: 'Website công ty',
              value: 'Website công ty',
            },
            {
              label: 'Website bán hàng',
              value: 'Website bán hàng',
            },
            {
              label: 'Website tuyển dụng',
              value: 'Website tuyển dụng',
            },
          ]"
          size="sm"
          variant="subtle"
          :disabled="false"
          label="Loại website"
          v-model="selectRepo"
        />
      </div>
    </div>
    <div class="py-4 grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
      <div class="rounded-md shadow-md" v-for="temp in listInterFace.data">
        <div>
          <a :href="'/interface-repository/' + temp.name">
            <span class="img-bg h-60 block relative overflow-hidden">
              <span
                class="img-skin rounded-t-md h-full bg-cover w-full bg-no-repeat absolute transition-all"
                v-bind:style="{
                  'background-image': 'url(' + temp.image_preview + ')',
                }"
              >
              </span>
            </span>
          </a>
        </div>
        <div class="p-6 pt-4">
          <h2 class="text-xl font-bold">
            {{ temp.name }}
          </h2>
          <div class="mt-4 flex justify-end">
            <Button
              :variant="'outline'"
              theme="gray"
              size="sm"
              label="Xem chi tiết"
              :route="'/interface-repository/' + temp.name"
            >
            </Button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import LayoutHeader from '@/components/LayoutHeader.vue'
import { Breadcrumbs, createResource } from 'frappe-ui'
import { onMounted, nextTick } from 'vue'
import { createToast, errorMessage } from '@/utils'

let title = 'Interface Repository'
const breadcrumbs = [{ label: title, route: { name: 'Interface Repository' } }]

//
let selectRepo = 'Tất cả'

const listInterFace = createResource({
  url: 'go1_cms.api.mbw_website_template.get_web_templates',
  params: { repo: selectRepo },
  cache: ['listInterFace', selectRepo],
  auto: true,
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
