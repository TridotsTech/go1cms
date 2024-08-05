<template>
  <LayoutHeader>
    <template #left-header>
      <Breadcrumbs :items="breadcrumbs" />
    </template>
    <template #right-header>
      <div class="flex flex-wrap justify-between items-center gap-2">
        <h2 class="font-bold text-3xl"></h2>
        <Button
          variant="solid"
          theme="blue"
          size="sm"
          label="Chọn giao diện này"
          @click="addWebTemplate"
        >
        </Button>
      </div>
    </template>
  </LayoutHeader>
  <div v-if="template.data" class="p-6 overflow-auto">
    <div v-if="template.data?.images.length" class="mb-10">
      <Carousel
        class="rounded-md"
        id="gallery"
        :items-to-show="1"
        v-model="currentSlide"
        :mouseDrag="false"
        :touchDrag="touchDrag"
      >
        <Slide v-for="slide in template.data?.images" :key="slide">
          <div class="carousel__item cursor-zoom-in">
            <photo-provider>
              <photo-consumer
                :intro="`Ảnh xem trước ${slide.idx}`"
                :key="slide.idx"
                :src="slide.image"
              >
                <img class="h-96 view-box" :src="slide.image" alt="" />
              </photo-consumer>
            </photo-provider>
          </div>
        </Slide>
      </Carousel>
      <Carousel
        class="mt-4 overflow-auto"
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

      <div class="text-center font-bold text-lg text-gray-700 my-10 italic">
        Ảnh xem trước
      </div>
    </div>
    <div class="mb-6" v-html="template.data?.content"></div>
  </div>
  <div v-else class="p-4 border border-gray-300 rounded-sm mb-4">
    <div class="flex justify-center h-screen mt-40 text-gray-700">
      <LoadingIndicator class="h-8 w-8" />
    </div>
  </div>
</template>

<script setup>
import { Carousel, Navigation, Slide } from 'vue3-carousel'
import 'vue3-carousel/dist/carousel.css'

import LayoutHeader from '@/components/LayoutHeader.vue'
import { Breadcrumbs, createResource, call } from 'frappe-ui'
import { ref, computed, watch } from 'vue'
import { createToast, errorMessage } from '@/utils'
import { useRouter } from 'vue-router'
const router = useRouter()
import { globalStore } from '@/stores/global'
const { changeLoadingValue } = globalStore()
import { useStorage } from '@vueuse/core'
const isSidebarCollapsed = useStorage('isSidebarCollapsed', false)

const props = defineProps({
  interfaceId: {
    type: String,
    required: true,
  },
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
    label: template.data?.template_name,
    route: {
      name: 'Interface Template',
      params: { interfaceId: props.interfaceId },
    },
  })
  return items
})
</script>
