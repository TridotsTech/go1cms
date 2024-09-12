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
            class="relative rounded-md shadow-md"
            v-for="temp in interFaces.data.data"
          >
            <div class="absolute top-6 left-4 z-[1]">
              <div
                v-if="temp.template_in_use"
                class="bg-green-100 shadow-lg p-2 rounded-lg text-green-700 font-bold text-base"
              >
                Đang sử dụng
              </div>
              <div
                v-else-if="temp.installed_template"
                class="bg-gray-100 shadow-lg p-2 rounded-lg text-orange-500 font-bold text-base"
              >
                Bản nháp
              </div>
              <div
                v-else
                class="bg-gray-100 shadow-lg p-2 rounded-lg text-black font-bold text-base"
              >
                Chưa cài đặt
              </div>
            </div>
            <div
              v-if="temp.template_in_use"
              class="absolute top-6 right-4 z-[1]"
            >
              <Tooltip text="Xem trang web" :hover-delay="1" :placement="'top'">
                <div>
                  <Button
                    variant="subtle"
                    theme="blue"
                    size="md"
                    label=""
                    icon="eye"
                    :link="
                      views.data?.config_domain?.use_other_domain
                        ? views.data?.config_domain?.domain + '/home'
                        : '/home'
                    "
                  >
                  </Button>
                </div>
              </Tooltip>
            </div>
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
                  class="img-skin rounded-t-md h-full bg-cover bg-top w-full bg-no-repeat absolute transition-all"
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
              <h2 class="text-xl font-bold">{{ temp.template_name }}</h2>
              <div class="mt-4 flex flex-wrap justify-end gap-2">
                <Button
                  v-if="temp.installed_template && !temp.template_in_use"
                  variant="solid"
                  theme="green"
                  size="sm"
                  label="Sử dụng trang web"
                  @click="() => handleModalUseTemplate(temp)"
                >
                </Button>
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
  <Dialog
    :options="{
      title: 'Sử dụng giao diện',
      actions: [
        {
          label: 'Xác nhận',
          variant: 'solid',
          theme: 'green',
          onClick: (close) => handleUseTemplate(close),
        },
      ],
    }"
    v-model="showModalUseTemplate"
  >
    <template v-slot:body-content>
      <div>
        <div>
          Bạn chắc chắn muốn sử dụng giao diện:
          <b>"{{ selectedItem?.template_name }}"</b>?
        </div>
        <div class="text-base text-red-600">
          <p>
            -
            <b
              >Dữ liệu từ mẫu đã sử dụng trước đó sẽ không được áp dụng khi
              chuyển đổi</b
            >.
          </p>
          <p>- <b>Mẫu này sẽ được sử dụng là website chính của bạn</b>.</p>
        </div>
      </div>
    </template>
  </Dialog>
</template>

<script setup>
import noImage from '@/assets/images/no_image.jpg'
import LayoutHeader from '@/components/LayoutHeader.vue'
import ViewControls from '@/components/ViewControls.vue'
import DisplayIcon from '@/components/Icons/DisplayIcon.vue'
import { Breadcrumbs, ListFooter, call } from 'frappe-ui'
import { createToast, errorMessage } from '@/utils'
import { ref, watch } from 'vue'
import { useRouter } from 'vue-router'
const router = useRouter()
import { globalStore } from '@/stores/global'
const { changeLoadingValue } = globalStore()
import { viewsStore } from '@/stores/views'
const { views } = viewsStore()

const breadcrumbs = [
  { label: 'Kho giao diện', route: { name: 'Interface Repository' } },
]

//
const interFaces = ref({})
const loadMore = ref(1)
const updatedPageCount = ref(20)

const showModalUseTemplate = ref(false)
const selectedItem = ref({})

const handleModalUseTemplate = (temp) => {
  selectedItem.value = temp
  showModalUseTemplate.value = true
}

const handleUseTemplate = async (close) => {
  changeLoadingValue(true, 'Đang cấu hình...')
  try {
    await call('go1_cms.api.client_website.set_primary_client_website', {
      name: selectedItem.value?.name,
    }).then(() => {
      createToast({
        title: 'Thành công',
        icon: 'check',
        iconClasses: 'text-green-600',
      })
      interFaces.value.reload()
      close()

      setTimeout(() => {
        window.location.reload()
      }, 300)
    })
  } catch (err) {
    if (err.messages && err.messages.length) {
      errorMessage('Có lỗi xảy ra', err.messages[0])
    } else {
      errorMessage('Có lỗi xảy ra', err)
    }
  }
  changeLoadingValue(false)
}

watch(
  () => interFaces.value?.data?.page_length_count,
  (val, oldVal) => {
    if (!val || val === oldVal) return
    updatedPageCount.value = val
  },
)
</script>
