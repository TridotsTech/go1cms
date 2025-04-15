<template>
  <LayoutHeader>
    <template #left-header>
      <Breadcrumbs :items="breadcrumbs" />
    </template>
    <template #right-header>
      <div class="flex gap-2 justify-end" v-if="alreadyActions">
        <Dropdown
          :options="[
            {
              group: __('Delete'),
              items: [
                {
                  label: __('Delete category'),
                  icon: 'trash',
                  onClick: () => {
                    showModalDelete = true
                  },
                },
              ],
            },
          ]"
        >
          <Button size="md">
            <template #icon>
              <FeatherIcon name="more-horizontal" class="h-4 w-4" />
            </template>
          </Button>
        </Dropdown>
        <Button
          variant="subtle"
          theme="gray"
          size="md"
          :label="__('Cancel')"
          @click="category.reload()"
          :disabled="!dirty"
        ></Button>
        <Button
          variant="solid"
          theme="blue"
          size="md"
          :label="__('Save')"
          @click="callUpdateDoc"
          :disabled="!dirty"
        ></Button>
      </div>
    </template>
  </LayoutHeader>
  <div class="p-6 overflow-auto">
    <div v-if="msgError" class="p-4 border border-gray-300 rounded-sm mb-4">
      <div class="text-base text-red-600 font-bold mb-2">
        {{ __('An error has occurred') }}:
      </div>
      <ErrorMessage :message="msgError" />
    </div>
    <div v-if="_category" class="p-4 border border-gray-300 rounded-sm mb-4">
      <div class="mb-5">
        <Fields :sections="sections" :data="_category" />
      </div>
    </div>
    <div v-else class="p-4 border border-gray-300 rounded-sm mb-4">
      <div class="flex justify-center h-screen mt-40 text-gray-700">
        <LoadingIndicator class="h-8 w-8" />
      </div>
    </div>
  </div>
  <Dialog
    :options="{
      title: __('Delete category'),
      actions: [
        {
          label: __('Delete'),
          variant: 'solid',
          theme: 'red',
          onClick: (close) => deleteDoc(close),
        },
      ],
    }"
    v-model="showModalDelete"
  >
    <template v-slot:body-content>
      <div>
        <div>
          {{ __('Are you sure you want to delete the category') }}:
          <b>"{{ _category?.category_title }}"</b>?
        </div>
        <div class="text-base">
          <p>
            <b class="text-red-600">- {{ __('Cannot be undone.') }}</b>
          </p>
        </div>
      </div>
    </template>
  </Dialog>
</template>

<script setup>
import Fields from '@/components/Fields.vue'
import LayoutHeader from '@/components/LayoutHeader.vue'
import {
  Breadcrumbs,
  call,
  createResource,
  ErrorMessage,
  Dropdown,
} from 'frappe-ui'
import { ref, computed, watch } from 'vue'
import { createToast, errorMessage, validErrApi } from '@/utils'
import { useRouter } from 'vue-router'
import { globalStore } from '@/stores/global'

const { changeLoadingValue } = globalStore()
const router = useRouter()
const props = defineProps({
  categoryId: {
    type: String,
    required: true,
  },
})
const msgError = ref()
const _category = ref({})
const showModalDelete = ref(false)

const sections = computed(() => {
  return [
    {
      section: 'sec 1',
      columns: 1,
      class: 'md:grid-cols-2',
      fields: [
        {
          label: 'Category name',
          mandatory: true,
          name: 'category_title',
          type: 'data',
          placeholder: 'Enter name',
        },
      ],
    },
    {
      section: 'sec 2',
      class: 'md:grid-cols-2',
      columns: 1,
      hideBorder: true,
      fields: [
        {
          label: 'Description',
          name: 'description',
          type: 'textarea',
          placeholder: 'Enter',
          rows: 10,
        },
      ],
    },
  ]
})

const category = createResource({
  url: 'go1_cms.api.category.get_category',
  params: {
    name: props.categoryId,
  },
  auto: true,
  transform: (data) => {
    _category.value = {
      ...data,
    }
    return data
  },
  onError: (err) => {
    validErrApi(err, router)
  },
})

// handle allow actions
const alreadyActions = ref(false)
const dirty = computed(() => {
  return JSON.stringify(category.data) !== JSON.stringify(_category.value)
})

watch(dirty, (val) => {
  alreadyActions.value = true
})

async function callUpdateDoc() {
  msgError.value = null

  const regex = /[&\/\\#+()$~%.`'":*?<>{}]/g
  if (regex.test(_category.value.category_title)) {
    msgError.value = `${__('Category name must not contain special characters:')} [&\/\\#+()$~%.\`'":*?<>{}]`
    return false
  }

  changeLoadingValue(true, __('Saving...'))
  try {
    const doc = await call('go1_cms.api.category.update_category', {
      data: {
        ..._category.value,
      },
    })
    if (doc.name) {
      createToast({
        title: __('Saved'),
        icon: 'check',
        iconClasses: 'text-green-600',
      })

      if (doc.name != props.categoryId) {
        router.push({
          name: 'Category Detail',
          params: { categoryId: doc.name },
        })
      } else {
        category.reload()
      }
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

async function deleteDoc(close) {
  changeLoadingValue(true, __('Deleting...'))
  try {
    await call('go1_cms.api.category.delete_category', {
      name: props.categoryId,
    }).then(() => {
      createToast({
        title: __('Deleted'),
        icon: 'check',
        iconClasses: 'text-green-600',
      })
      close()
      router.push({
        name: 'Categories',
      })
    })
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

watch(
  () => props.categoryId,
  (val) => {
    category.update({
      params: { name: val },
    })
    category.reload()
  },
)

// breadcrumbs
const breadcrumbs = computed(() => {
  let items = [
    { label: __('Category management'), route: { name: 'Categories' } },
  ]
  items.push({
    label: category.data?.name,
    route: {},
  })
  return items
})
</script>
