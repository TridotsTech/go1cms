<template>
  <LayoutHeader>
    <template #left-header>
      <Breadcrumbs :items="breadcrumbs" />
    </template>
  </LayoutHeader>
  <div class="flex-1 flex flex-col h-full p-6 pt-2 pb-4 overflow-auto">
    <div>
      <ViewControls
        v-model="interFaces"
        v-model:loadMore="loadMore"
        v-model:updatedPageCount="updatedPageCount"
        doctype="MBW Website Template"
        :options="{
          hideColumnsButton: true,
        }"
      />
    </div>
    <div class="flex-1 flex" v-if="interFaces?.data?.data?.length">
      <div class="w-full">
        <div class="p-4 grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-8">
          <div
            class="rounded-md shadow-md"
            v-for="temp in interFaces.data.data"
          >
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
                  v-if="temp.image_preview"
                  class="img-skin rounded-t-md h-full bg-cover w-full bg-no-repeat absolute transition-all"
                  :style="{
                    backgroundImage: `url('${temp.image_preview}')`,
                  }"
                >
                </span>
                <span
                  v-else
                  class="img-skin rounded-t-md h-full bg-cover w-full bg-no-repeat absolute transition-all"
                  :style="{
                    backgroundImage: `url('${noImage}')`,
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
      </div>
    </div>
    <ListFooter
      v-if="interFaces.data?.data?.length"
      class="border-t px-5 py-2"
      v-model="interFaces.data.page_length_count"
      :options="{
        rowCount: interFaces.data.row_count,
        totalCount: interFaces.data.total_count,
      }"
      @loadMore="() => loadMore++"
    />
    <div v-else class="flex flex-1 items-center justify-center">
      <div
        class="flex flex-col items-center gap-3 text-xl font-medium text-gray-500"
      >
        <DisplayIcon class="h-10 w-10" />
        <span>{{
          __('Giao diện đang được cập nhật thêm, vui lòng quay lại sau')
        }}</span>
      </div>
    </div>
  </div>
</template>

<script setup>
import noImage from '@/assets/images/no_image.jpg'
import LayoutHeader from '@/components/LayoutHeader.vue'
import ViewControls from '@/components/ViewControls.vue'
import DisplayIcon from '@/components/Icons/DisplayIcon.vue'
import { Breadcrumbs, ListFooter } from 'frappe-ui'
import { ref, watch } from 'vue'
import { useRouter } from 'vue-router'
const router = useRouter()

const breadcrumbs = [
  { label: 'Kho giao diện', route: { name: 'Interface Repository' } },
]

//
const interFaces = ref({})
const loadMore = ref(1)
const updatedPageCount = ref(20)

watch(
  () => interFaces.value?.data?.page_length_count,
  (val, old_value) => {
    if (!val || val === old_value) return
    updatedPageCount.value = val
  }
)
</script>
