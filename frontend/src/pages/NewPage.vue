<template>
  <LayoutHeader>
    <template #left-header>
      <Breadcrumbs :items="breadcrumbs" />
    </template>
    <template #right-header>
      <div v-if="pageExists && alreadyActions" class="flex gap-2 justify-end">
        <Button
          variant="subtle"
          theme="gray"
          size="md"
          :label="__('Cancel')"
          :disabled="!dirty"
          @click="cancelSaveDoc"
        ></Button>
        <Button
          :variant="'solid'"
          theme="blue"
          size="md"
          :label="__('Save')"
          :disabled="!dirty"
          @click="callUpdateDoc"
        >
        </Button>
        <Button
          variant="subtle"
          theme="green"
          size="md"
          :label="__('Create page')"
          :disabled="dirty"
          @click="showDialogCreate = true"
        >
        </Button>
      </div>
    </template>
  </LayoutHeader>
  <div ref="refToTop" class="p-6 overflow-auto">
    <div v-if="msgError" class="p-4 border border-gray-300 rounded-sm mb-4">
      <div class="text-base text-red-600 font-bold mb-2">
        {{ __('An error has occurred') }}:
      </div>
      <ErrorMessage :message="msgError" />
    </div>
    <div v-if="pageExists">
      <FieldsComponent v-model="_page.fields_cp"></FieldsComponent>
      <FieldsSectionComponent
        v-model="_page.fields_st_cp"
      ></FieldsSectionComponent>
    </div>
    <div v-else class="p-4 border border-gray-300 rounded-sm mb-4">
      <div
        class="flex justify-center h-screen mt-40 text-gray-700"
        v-if="!alreadyActions"
      >
        <LoadingIndicator class="h-8 w-8" />
      </div>
      <div v-else>
        {{ __('No templates available for creating a new page.') }}
      </div>
    </div>
  </div>
  <Dialog v-model="showDialogCreate" :options="{ size: 'xl' }">
    <template #body-title>
      <h3>{{ __('Page information') }}</h3>
    </template>
    <template #body-content>
      <div class="grid grid-cols-1 gap-4">
        <div>
          <div class="mb-2">
            <label for="name_page" class="text-sm text-gray-600">
              {{ __('Website name') }}
              <span class="text-red-500">*</span>
            </label>
          </div>
          <FormControl
            id="name_page"
            type="text"
            :placeholder="__('Enter')"
            v-model="namePage"
          />
        </div>
        <div class="flex flex-col gap-2">
          <div>
            <div class="mb-2">
              <label for="route_page" class="text-sm text-gray-600">
                {{ __('Redirect link') }}
              </label>
            </div>
            <FormControl
              class="flex-auto"
              id="route_page"
              type="text"
              :placeholder="__('Enter')"
              v-model="routePage"
            />
          </div>
          <div v-if="routePage" class="text-base">
            <span class="text-gray-700">{{ route_prefix }}</span>
            <span class="font-bold">{{ customSlugify(routePage) }}</span>
          </div>
        </div>
        <ErrorMessage :message="msgErrorDialog" />
      </div>
    </template>
    <template #actions>
      <div class="flex justify-end gap-2">
        <Button @click="showDialogCreate = false"> {{ __('Close') }} </Button>
        <Button theme="blue" variant="solid" @click="handleCreatePage">
          {{ __('Create') }}
        </Button>
      </div>
    </template>
  </Dialog>
</template>

<script setup>
import LayoutHeader from '@/components/LayoutHeader.vue'
import FieldsComponent from '@/components/FieldsPage/FieldsComponent.vue'
import FieldsSectionComponent from '@/components/FieldsPage/FieldsSectionComponent.vue'
import {
  Breadcrumbs,
  ErrorMessage,
  createResource,
  call,
  FormControl,
} from 'frappe-ui'
import { ref, computed, watch } from 'vue'
import {
  createToast,
  errorMessage,
  handleUploadFieldImage,
  customSlugify,
  validErrApi,
} from '@/utils'
import { globalStore } from '@/stores/global'
import { useRouter } from 'vue-router'
const router = useRouter()

const { changeLoadingValue } = globalStore()

const _page = ref({})
const msgError = ref()
const refToTop = ref(null)
const showDialogCreate = ref(false)
const route_prefix = ref('')
const alreadyActions = ref(false)

// get detail
const page = createResource({
  url: 'go1_cms.api.new_page.get_info_template_page',
  method: 'GET',
  auto: true,
  transform: (data) => {
    route_prefix.value = data?.web_page?.route_prefix
    _page.value = JSON.parse(JSON.stringify(data))
    alreadyActions.value = true
    return data
  },
  onError: (err) => {
    validErrApi(err, router)

    if (err.messages && err.messages.length) {
      msgError.value = err.messages.join(', ')
      errorMessage(__('An error has occurred'), err.messages.join(', '))
    } else {
      errorMessage(__('An error has occurred'), err)
    }
  },
})

// handle allow actions
const dirty = computed(() => {
  if (JSON.stringify(_page.value) == '{}') {
    return false
  }
  return JSON.stringify(page.data) !== JSON.stringify(_page.value)
})
const pageExists = computed(() => {
  return JSON.stringify(_page.value) !== '{}'
})

const breadcrumbs = [{ label: __('Add New Page'), route: { name: 'New Page' } }]

async function callUpdateDoc() {
  changeLoadingValue(true, __('Saving...'))
  try {
    let data = JSON.parse(JSON.stringify(_page.value))
    // upload image
    await handleUploadFieldImage(
      data,
      _page,
      'Web Page Builder',
      _page.value?.web_page?.doc_page,
    )

    let docUpdate = await call(
      'go1_cms.api.new_page.update_info_template_page',
      {
        data: data,
      },
    )

    if (docUpdate.name) {
      page.reload()

      createToast({
        title: __('Saved'),
        icon: 'check',
        iconClasses: 'text-green-600',
      })
    }
  } catch (err) {
    validErrApi(err, router)

    if (err.messages && err.messages.length) {
      msgError.value = err.messages.join(', ')
      errorMessage(__('An error has occurred'), err.messages.join(', '))
    } else {
      errorMessage(__('An error has occurred'), err)
    }
  }
  changeLoadingValue(false)
}

async function cancelSaveDoc() {
  await page.reload()
}

// create page, handle slug
const namePage = ref('')
const routePage = ref('')
const msgErrorDialog = ref()

watch(namePage, (val) => {
  routePage.value = customSlugify(val)
})

async function handleCreatePage() {
  try {
    msgErrorDialog.value = ''
    if (!namePage.value) {
      msgErrorDialog.value = __('Website name') + ' ' + __('cannot be empty')
      return false
    }
    changeLoadingValue(true, __('Creating page...'))

    let docCreate = await call('go1_cms.api.new_page.create_new_page', {
      name: _page.value?.web_page?.doc_page,
      name_page: namePage.value,
      route_page: routePage.value,
    })

    if (docCreate.name) {
      createToast({
        title: __('Success'),
        icon: 'check',
        iconClasses: 'text-green-600',
      })
      window.location.href = `/cms/page?view=${docCreate.name}`
    }
  } catch (err) {
    validErrApi(err, router)

    if (err.messages && err.messages.length) {
      msgError.value = err.messages.join(', ')
      errorMessage(__('An error has occurred'), err.messages.join(', '))
    } else {
      errorMessage(__('An error has occurred'), err)
    }
  }
  changeLoadingValue(false)
}
</script>
