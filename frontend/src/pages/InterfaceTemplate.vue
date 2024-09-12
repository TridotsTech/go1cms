<template>
  <LayoutHeader>
    <template #left-header>
      <Breadcrumbs :items="breadcrumbs" />
    </template>
    <template #right-header>
      <div v-if="alreadyActions" class="flex flex-wrap items-center gap-2">
        <div
          v-if="template.data?.installed_template"
          class="flex flex-wrap items-center gap-2"
        >
          <Dropdown :options="opstionsDropdown">
            <Button size="md">
              <template #icon>
                <FeatherIcon name="more-horizontal" class="h-4 w-4" />
              </template>
            </Button>
          </Dropdown>
          <Button
            v-if="!template.data?.template_in_use"
            variant="solid"
            theme="green"
            size="sm"
            label="Sử dụng trang web"
            @click="handleModalUseTemplate"
          >
          </Button>
        </div>
        <div v-if="template.data?.template_in_use">
          <Tooltip text="Xem trang web" :hover-delay="1" placement="top">
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
        <Button
          v-if="!template.data?.installed_template"
          variant="solid"
          theme="blue"
          size="sm"
          label="Cài đặt giao diện"
          @click="addWebTemplate"
        >
        </Button>
      </div>
    </template>
  </LayoutHeader>
  <div v-if="template.data" class="overflow-auto">
    <div class="sticky top-0 z-[1] flex justify-end">
      <div class="bg-white">
        <div
          class="flex flex-col gap-2 p-4 border-l border-b border-gray-300 min-w-64 rounded-bl-lg text-base text-gray-700"
        >
          <div>
            <strong>Trạng thái:</strong>
            <span v-if="!template.data?.installed_template" class="text-black">
              Chưa cài đặt</span
            >
            <span
              v-else-if="template.data?.template_in_use"
              class="text-green-700"
            >
              Đang sử dụng</span
            >
            <span v-else class="text-orange-500"> Bản nháp</span>
          </div>
          <div v-if="template.data?.template_in_use">
            <strong>Trang web:</strong>
            <span
              v-if="template.data?.client_web.published"
              class="text-blue-700"
            >
              Đang kích hoạt</span
            >
            <span v-else class="text-orange-500"> Dừng kích hoạt</span>
          </div>
        </div>
      </div>
    </div>
    <div v-if="template.data?.images.length" class="p-6 pb-2 mb-6">
      <div
        class="flex flex-wrap justify-center font-bold text-lg text-gray-700 italic border border-b-0 rounded-t-md border-gray-300"
      >
        <p class="p-3">Ảnh xem trước</p>
      </div>
      <div
        class="py-4 rounded-b-md border border-gray-300 focus-visible:outline-none"
      >
        <Carousel
          class="p-2 pt-4 focus-visible:outline-none"
          id="gallery"
          :items-to-show="1"
          v-model="currentSlide"
          :mouseDrag="false"
          :touchDrag="touchDrag"
        >
          <Slide v-for="slide in template.data?.images" :key="slide">
            <div class="carousel__item cursor-zoom-in">
              <photo-provider :loop="true">
                <photo-consumer
                  v-for="src in template.data?.images"
                  :intro="`Ảnh xem trước ${src.idx}`"
                  :key="src.idx"
                  :src="src.image"
                >
                  <img
                    v-if="src.idx == slide.idx"
                    class="h-96 view-box"
                    :src="src.image"
                    alt=""
                  />
                </photo-consumer>
              </photo-provider>
            </div>
          </Slide>
        </Carousel>
        <div class="my-2 border-t border-dashed border-gray-300"></div>
        <Carousel
          class="p-2 focus-visible:outline-none"
          id="thumbnails"
          v-model="currentSlide"
          :items-to-show="1"
          :breakpoints="breakpoints"
          :touchDrag="touchDrag"
        >
          <Slide v-for="slide in template.data?.images" :key="slide">
            <div
              class="carousel__item cursor-pointer mx-6 px-6 py-2 border-2 rounded-md w-[200px]"
              :class="currentSlide == slide.idx - 1 ? 'border-red-500' : ''"
              @click="slideTo(slide.idx - 1)"
            >
              <img class="h-24" :src="slide.image" alt="" />
            </div>
          </Slide>
          <template #addons>
            <Navigation />
          </template>
        </Carousel>
      </div>
    </div>
    <div class="p-6">
      <div
        class="flex flex-wrap justify-center font-bold text-lg text-gray-700 italic border border-b-0 rounded-t-md border-gray-300"
      >
        <p class="p-3">Mô tả</p>
      </div>
      <div
        class="rounded-b-md mb-6 p-4 border border-gray-300"
        v-html="template.data?.content"
      ></div>
    </div>
  </div>
  <div v-else class="p-4 border border-gray-300 rounded-sm mb-4">
    <div class="flex justify-center h-screen mt-40 text-gray-700">
      <LoadingIndicator class="h-8 w-8" />
    </div>
  </div>

  <!-- dialog delete -->
  <Dialog
    :options="{
      title: 'Xóa trang web',
      actions: [
        {
          label: 'Xác nhận',
          variant: 'solid',
          theme: 'red',
          onClick: (close) => deleteDoc(close),
        },
      ],
    }"
    v-model="showDialogDelete"
  >
    <template v-slot:body-content>
      <div>
        <div>
          Bạn chắc chắn muốn xóa website đã tạo từ mẫu:
          <b>"{{ template.data?.template_name }}"</b>?
        </div>
        <div class="text-base text-red-600">
          <p>
            -
            <b>
              Điều nãy sẽ xóa toàn bộ dữ liệu đã cài đặt cho trang web trước
              đó</b
            >.
          </p>
          <p>
            -
            <b>
              Sau khi xóa, sẽ không vào được trang web nếu trang web đang sử
              dụng</b
            >.
          </p>
          <p>- <b> Không thể hoàn tác</b>.</p>
        </div>
      </div>
    </template>
  </Dialog>
  <!-- dialog use web -->
  <Dialog
    :options="{
      title: 'Sử dụng trang web',
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
          Bạn chắc chắn muốn sử dụng trang web:
          <b>"{{ template.data?.template_name }}"</b>?
        </div>
        <div class="text-base text-red-600">
          <p>
            -
            <b
              >Dữ liệu từ trang web đã sử dụng trước đó sẽ không được áp dụng
              khi chuyển đổi</b
            >.
          </p>
          <p>
            - <b>Trang web này sẽ được sử dụng là trang web chính của bạn</b>.
          </p>
        </div>
      </div>
    </template>
  </Dialog>
  <!-- dialog set publish -->
  <Dialog
    :options="{
      title: template.data?.client_web.published
        ? 'Dừng kích hoạt trang web'
        : 'Kích hoạt trang web',
      actions: [
        {
          label: 'Xác nhận',
          variant: 'solid',
          theme: 'red',
          onClick: (close) => setPublishedMyWebsite(close),
        },
      ],
    }"
    v-model="showDialogSetPublish"
  >
    <template v-slot:body-content>
      <div>
        <div
          v-if="template.data?.client_web.published"
          class="text-base text-red-600"
        >
          <p>
            -
            <b>Sau khi dừng kích hoạt, trang web sẽ không thể vào được</b>.
          </p>
        </div>
        <div v-else class="text-base text-blue-600">
          <p>- <b>Sau khi kích hoạt, trang web sẽ hoạt động trở lại</b>.</p>
        </div>
      </div>
    </template>
  </Dialog>
</template>

<script setup>
import { Carousel, Navigation, Slide } from 'vue3-carousel'
import 'vue3-carousel/dist/carousel.css'

import LayoutHeader from '@/components/LayoutHeader.vue'
import { Breadcrumbs, createResource, call, Dropdown } from 'frappe-ui'
import { ref, computed, watch } from 'vue'
import { createToast, errorMessage } from '@/utils'
// import { useRouter } from 'vue-router'
// const router = useRouter()
import { globalStore } from '@/stores/global'
const { changeLoadingValue } = globalStore()
import { useStorage } from '@vueuse/core'
const isSidebarCollapsed = useStorage('isSidebarCollapsed', false)
import { viewsStore } from '@/stores/views'
const { views } = viewsStore()

const props = defineProps({
  interfaceId: {
    type: String,
    required: true,
  },
})

const alreadyActions = computed(() => {
  return template.data ? true : false
})

// slider
const currentSlide = ref(0)
const breakpoints = ref({
  640: { itemsToShow: 2 },
  1024: { itemsToShow: 3 },
  1280: { itemsToShow: 4 },
  1536: { itemsToShow: 5 },
})

const slideTo = (val) => {
  currentSlide.value = val
}
const touchDrag = ref(false)

watch(isSidebarCollapsed, () => {
  setTimeout(() => {
    touchDrag.value = !touchDrag.value
  }, 150)
})

// set publish web
const showDialogSetPublish = ref(false)
async function setPublishedMyWebsite(close) {
  let loadingText = 'Đang kích hoạt website...'
  if (template.data?.client_web.published == 1) {
    loadingText = 'Đang dừng kích hoạt website...'
  }

  changeLoadingValue(true, loadingText)
  try {
    await call('go1_cms.api.client_website.update_published_client_website', {
      name: template.data?.name,
      published: template.data?.client_web.published == 1 ? 0 : 1,
    }).then(() => {
      createToast({
        title: 'Thành công',
        icon: 'check',
        iconClasses: 'text-green-600',
      })
      template.reload()
      close()
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

// delete web
const showDialogDelete = ref(false)
async function deleteDoc(close) {
  changeLoadingValue(true, 'Đang xóa...')
  try {
    await call('go1_cms.api.client_website.delete_client_website', {
      name: template.data?.name,
    }).then(() => {
      createToast({
        title: 'Xóa thành công',
        icon: 'check',
        iconClasses: 'text-green-600',
      })
      close()
      if (template.data?.template_in_use == 1) {
        views.reload()
        setTimeout(() => window.location.reload(), 300)
      } else {
        template.reload()
      }
    })
  } catch (err) {
    if (err.messages && err.messages.length) {
      errorMessage('Có lỗi xảy ra', err.messages.join(', '))
    } else {
      errorMessage('Có lỗi xảy ra', err)
    }
  }
  changeLoadingValue(false)
}

// set use web
const showModalUseTemplate = ref(false)

const handleModalUseTemplate = () => {
  showModalUseTemplate.value = true
}

const handleUseTemplate = async (close) => {
  changeLoadingValue(true, 'Đang cấu hình...')
  try {
    await call('go1_cms.api.client_website.set_primary_client_website', {
      name: template.data?.name,
    }).then(() => {
      createToast({
        title: 'Thành công',
        icon: 'check',
        iconClasses: 'text-green-600',
      })
      template.reload()
      close()
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

// get detail
const template = createResource({
  url: 'go1_cms.api.mbw_website_template.get_web_template',
  method: 'GET',
  params: { name: props.interfaceId },
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
        setTimeout(() => {
          window.location.reload()
        }, 300)
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
    label: template.data?.template_name,
    route: {
      name: 'Interface Template',
      params: { interfaceId: props.interfaceId },
    },
  })
  return items
})

const opstionsDropdown = computed(() => {
  let ops = [
    {
      group: 'Xóa',
      items: [
        {
          label: 'Xóa trang web',
          icon: 'trash',
          onClick: () => {
            showDialogDelete.value = true
          },
        },
      ],
    },
  ]
  if (template.data?.template_in_use) {
    ops.unshift({
      group: 'Trang web',
      items: [
        {
          label: template.data?.client_web.published
            ? 'Dừng kích hoạt'
            : 'Kích hoạt',
          icon: 'globe',
          onClick: () => {
            showDialogSetPublish.value = true
          },
        },
      ],
    })
  }

  return ops
})
</script>
