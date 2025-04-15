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
            :label="__('Use website')"
            @click="handleModalUseTemplate"
          >
          </Button>
        </div>
        <div v-if="template.data?.template_in_use">
          <Tooltip :text="__('View Website')" :hover-delay="1" placement="top">
            <div>
              <Button
                variant="subtle"
                theme="blue"
                size="md"
                label=""
                icon="eye"
                :link="views.data?.config_domain?.domain + '/home'"
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
          :label="__('Install Interface')"
          @click="prepareFileTemplate"
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
            <strong>{{ __('Status') }}: </strong>
            <span v-if="!template.data?.installed_template" class="text-black">
              {{ __('Not Installed') }}
            </span>
            <span
              v-else-if="template.data?.template_in_use"
              class="text-green-700"
            >
              {{ __('In Use') }}</span
            >
            <span v-else class="text-orange-500">{{ __('Draft') }}</span>
          </div>
          <div v-if="template.data?.template_in_use">
            <strong>{{ __('Website') }}: </strong>
            <span
              v-if="template.data?.client_web.published"
              class="text-blue-700"
            >
              {{ __('Activating') }}
            </span>
            <span v-else class="text-orange-500">{{ __('Deactivating') }}</span>
          </div>
        </div>
      </div>
    </div>
    <div v-if="template.data?.images.length" class="p-6 pb-2 mb-6">
      <div
        class="flex flex-wrap justify-center font-bold text-lg text-gray-700 italic border border-b-0 rounded-t-md border-gray-300"
      >
        <p class="p-3">{{ __('Preview Image') }}</p>
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
                  :intro="`Image ${src.idx}`"
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
        <p class="p-3">{{ __('Description') }}</p>
      </div>
      <div
        class="rounded-b-md mb-6 p-4 border border-gray-300"
        v-html="template.data?.content"
      ></div>
    </div>
    <div class="min-h-[200px]"></div>
  </div>
  <div v-else class="p-4 border border-gray-300 rounded-sm mb-4">
    <div class="flex justify-center h-screen mt-40 text-gray-700">
      <LoadingIndicator class="h-8 w-8" />
    </div>
  </div>

  <!-- dialog delete -->
  <Dialog
    :options="{
      title: __('Delete Website'),
      actions: [
        {
          label: __('Confirm'),
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
          {{
            __(
              'Are you sure you want to delete the website created from the template',
            )
          }}: <b>"{{ template.data?.template_name }}"</b>?
        </div>
        <div class="text-base text-red-600">
          <p>
            -
            <b>
              {{
                __(
                  'This will delete all previously installed data for the website.',
                )
              }}
            </b>
          </p>
          <p>
            -
            <b>
              {{
                __(
                  'After deletion, the website will no longer be accessible if it is currently in use.',
                )
              }}
            </b>
          </p>
          <p>
            - <b> {{ __('Cannot be undone.') }}</b>
          </p>
        </div>
      </div>
    </template>
  </Dialog>
  <!-- dialog use web -->
  <Dialog
    :options="{
      title: __('Use website'),
      actions: [
        {
          label: __('Confirm'),
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
          {{ __('Are you sure you want to use the website') }}:
          <b>"{{ template.data?.template_name }}"</b>?
        </div>
        <div class="text-base text-red-600">
          <p>
            -
            <b>
              {{
                __(
                  'Data from the previously used website will not be applied during the switch.',
                )
              }}
            </b>
          </p>
          <p>
            -
            <b>
              {{ __('This website will be set as your primary website.') }}</b
            >
          </p>
        </div>
      </div>
    </template>
  </Dialog>
  <!-- dialog set publish -->
  <Dialog
    :options="{
      title: template.data?.client_web.published
        ? __('Deactivate Website')
        : __('Activate Website'),
      actions: [
        {
          label: __('Confirm'),
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
            <b>
              {{
                __(
                  'After deactivation, the website will no longer be accessible.',
                )
              }}
            </b>
          </p>
        </div>
        <div v-else class="text-base text-blue-600">
          <p>
            -<b>
              {{
                __('After activation, the website will become active again.')
              }}</b
            >
          </p>
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
import { createToast, errorMessage, validErrApi } from '@/utils'
import { useRouter } from 'vue-router'
const router = useRouter()
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
  let loadingText = __('Activating website...')
  if (template.data?.client_web.published == 1) {
    loadingText = __('Deactivating website...')
  }

  changeLoadingValue(true, loadingText)
  try {
    await call('go1_cms.api.client_website.update_published_client_website', {
      name: template.data?.name,
      published: template.data?.client_web.published == 1 ? 0 : 1,
    }).then(() => {
      createToast({
        title: __('Success'),
        icon: 'check',
        iconClasses: 'text-green-600',
      })
      template.reload()
      close()
    })
  } catch (err) {
    validErrApi(err, router)

    if (err.messages && err.messages.length) {
      errorMessage(__('An error has occurred'), err.messages[0])
    } else {
      errorMessage(__('An error has occurred'), err)
    }
  }
  changeLoadingValue(false)
}

// delete web
const showDialogDelete = ref(false)
async function deleteDoc(close) {
  changeLoadingValue(true, __('Deleting...'))
  try {
    await call('go1_cms.api.client_website.delete_client_website', {
      name: template.data?.name,
    }).then(() => {
      createToast({
        title: __('Deleted'),
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
    validErrApi(err, router)

    if (err.messages && err.messages.length) {
      errorMessage(__('An error has occurred'), err.messages.join(', '))
    } else {
      errorMessage(__('An error has occurred'), err)
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
  changeLoadingValue(true, __('Configuring...'))
  try {
    await call('go1_cms.api.client_website.set_primary_client_website', {
      name: template.data?.name,
    }).then(() => {
      createToast({
        title: __('Success'),
        icon: 'check',
        iconClasses: 'text-green-600',
      })
      template.reload()
      close()

      setTimeout(() => {
        window.location.reload()
      }, 300)
    })
  } catch (err) {
    validErrApi(err, router)

    if (err.messages && err.messages.length) {
      errorMessage(__('An error has occurred'), err.messages[0])
    } else {
      errorMessage(__('An error has occurred'), err)
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
  onError: (err) => {
    validErrApi(err, router)

    if (err.messages && err.messages.length) {
      errorMessage(__('An error has occurred'), err.messages.join(', '))
    } else {
      errorMessage(__('An error has occurred'), err)
    }
  },
})

async function prepareFileTemplate() {
  changeLoadingValue(true, __('Loading interface...'))
  try {
    await call('go1_cms.api.mbw_website_template.prepare_file_template', {
      name: props.interfaceId,
    }).then((d) => {
      if (d.code == 200) {
        addWebTemplate()
      } else {
        changeLoadingValue(false)
        errorMessage(__('An error has occurred'), d.msg)
      }
    })
  } catch (err) {
    changeLoadingValue(false)
    if (err.messages && err.messages.length) {
      errorMessage(__('An error has occurred'), err.messages[0])
    }
  }
}

// add web template
async function addWebTemplate() {
  changeLoadingValue(true, __('Installing interface...'))
  try {
    await call('go1_cms.api.mbw_website_template.create_client_website', {
      name: props.interfaceId,
    }).then((d) => {
      if (d) {
        createToast({
          title: __('Success'),
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
      errorMessage(__('An error has occurred'), err.messages[0])
    }
  }
}

const breadcrumbs = computed(() => {
  let items = [
    {
      label: __('Interface Repository'),
      route: { name: 'Interface Repository' },
    },
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
      group: __('Delete'),
      items: [
        {
          label: __('Delete Website'),
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
      group: __('Website'),
      items: [
        {
          label: template.data?.client_web.published
            ? __('Deactivate')
            : __('Activate'),
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
