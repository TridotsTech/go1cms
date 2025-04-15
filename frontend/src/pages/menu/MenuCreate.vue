<template>
  <LayoutHeader>
    <template #left-header>
      <Breadcrumbs :items="breadcrumbs" />
    </template>
    <template #right-header>
      <div class="flex rounded-sm gap-2 justify-end">
        <Button
          variant="subtle"
          theme="gray"
          size="md"
          :label="__('Cancel')"
          route="/menu"
        ></Button>
        <Button
          variant="solid"
          theme="blue"
          size="md"
          :label="__('Save')"
          @click="callInsertDoc"
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
    <div class="p-4 border border-gray-300 rounded-sm mb-4">
      <div class="mb-5">
        <Fields :sections="sections" :data="_menu" />
      </div>
      <div>
        <p class="text-sm text-gray-600 mb-2">{{ __('Menu list') }}</p>
        <DraggableNested
          v-model="_menu.menus"
          :maxLevel="3"
          v-model:countId="countId"
        ></DraggableNested>
      </div>
    </div>
  </div>
</template>

<script setup>
import Fields from '@/components/Fields.vue'
import LayoutHeader from '@/components/LayoutHeader.vue'
import DraggableNested from '@/components/DraggableNested.vue'
import { Breadcrumbs, call, ErrorMessage } from 'frappe-ui'
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { createToast, errorMessage, validErrApi } from '@/utils'
import { globalStore } from '@/stores/global'
const { changeLoadingValue } = globalStore()

const router = useRouter()
const breadcrumbs = [
  { label: 'Menu', route: { name: 'Menu' } },
  { label: __('Add New'), route: {} },
]

let _menu = ref({
  menus: [],
})
const countId = ref(0)
const msgError = ref()

const sections = computed(() => {
  return [
    {
      section: 'menu Name',
      columns: 1,
      class: 'md:grid-cols-2',
      fields: [
        {
          label: 'Menu name',
          mandatory: true,
          name: 'title',
          type: 'data',
          placeholder: 'Enter name',
        },
      ],
    },
  ]
})

function extractMenus(data) {
  let elementsArray = []
  let level = 0
  let idx = 0

  function recurse(elements, parentId = '') {
    level++
    for (let element of elements) {
      idx++
      if (element.elements.length) {
        element['is_mega_menu'] = 1
        if (level == 1 && element.no_of_column <= 0) {
          element['no_of_column'] = 1
        }
      }
      if (level > 1) {
        element['parent_menu'] = parentId
      }
      element['menu_id'] = idx
      element['idx'] = idx

      elementsArray.push(element)
      if (element.elements && element.elements.length > 0) {
        recurse(element.elements, element.idx)
      }
    }
  }

  recurse(data)
  return elementsArray
}

async function callInsertDoc() {
  msgError.value = null

  let menuUpdate = { ..._menu.value, menus: extractMenus(_menu.value.menus) }

  if (!menuUpdate.title) {
    msgError.value = __('Menu name') + ' ' + __('cannot be empty')
    errorMessage(
      __('An error has occurred'),
      __('Menu name') + ' ' + __('cannot be empty'),
    )
    return
  }

  changeLoadingValue(true, __('Saving...'))
  try {
    const doc = await call('go1_cms.api.menu.create_menu', {
      data: {
        ...menuUpdate,
      },
    })
    createToast({
      title: __('Saved'),
      icon: 'check',
      iconClasses: 'text-green-600',
    })
    doc.name &&
      router.push({
        name: 'Menu Detail',
        params: { menuId: doc.name },
      })
  } catch (err) {
    validErrApi(err, router)
    msgError.value = err.messages.join(', ')
    errorMessage(__('An error has occurred'), err.messages.join(', '))
  }
  changeLoadingValue(false)
}
</script>
