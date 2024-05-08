<template>
  <LayoutHeader>
    <template #left-header>
      <Breadcrumbs :items="breadcrumbs" />
    </template>
  </LayoutHeader>
  <div class="p-6">
    <div class="border-b border-gray-300 pb-2">
      <div class="grid grid-cols-1 lg:grid-cols-4 sm:grid-cols-2">
        <FormControl
          type="select"
          :options="[
            {
              label: 'Tất cả',
              value: 'all',
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
    <div
      v-if="listInterFace.data && listInterFace.data.length"
      class="py-4 grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8"
    >
      <div class="rounded-md shadow-md" v-for="temp in listInterFace.data">
        <div
          class="cursor-pointer"
          :onclick="
            () => {
              router.push({
                name: 'Interface Template',
                params: { interfaceId: temp.name },
              })
            }
          "
        >
          <span class="img-bg h-60 block relative overflow-hidden">
            <span
              class="img-skin rounded-t-md h-full bg-cover w-full bg-no-repeat absolute transition-all"
              v-bind:style="{
                'background-image': 'url(' + temp.image_preview + ')',
              }"
            >
            </span>
          </span>
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
    <div v-else>
      <div class="flex h-60 items-center justify-center">
        Chúng tôi đang cập nhật thêm giao diện, vui lòng vào lại sau.
      </div>
    </div>
  </div>
</template>

<script setup>
import LayoutHeader from '@/components/LayoutHeader.vue'
import { Breadcrumbs, createResource } from 'frappe-ui'
import { onMounted, nextTick, ref } from 'vue'
import { createToast, errorMessage } from '@/utils'
import { useRouter } from 'vue-router'
const router = useRouter()

const breadcrumbs = [
  { label: 'Kho giao diện', route: { name: 'Interface Repository' } },
]

//
const selectRepo = ref('all')

const listInterFace = createResource({
  url: 'go1_cms.api.mbw_website_template.get_web_templates',
  method: 'GET',
  params: { repo: selectRepo.value },
  cache: ['listInterFace', selectRepo.value],
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
