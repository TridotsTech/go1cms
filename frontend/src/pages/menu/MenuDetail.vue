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
                  label: __('Delete menu'),
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
          @click="menu.reload()"
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
    <div v-if="_menu" class="p-4 border border-gray-300 rounded-sm mb-4">
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
    <div v-else class="p-4 border border-gray-300 rounded-sm mb-4">
      <div class="flex justify-center h-screen mt-40 text-gray-700">
        <LoadingIndicator class="h-8 w-8" />
      </div>
    </div>
  </div>
  <Dialog
    :options="{
      title: __('Delete menu'),
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
          {{ __('Are you sure you want to delete the menu') }}:
          <b>"{{ _menu?.title }}"</b>?
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
import { createToast, errorMessage, warningMessage, validErrApi } from '@/utils'
import { useRouter } from 'vue-router'
const router = useRouter()
import DraggableNested from '@/components/DraggableNested.vue'
import { globalStore } from '@/stores/global'

const { changeLoadingValue } = globalStore()
const props = defineProps({
  menuId: {
    type: String,
    required: true,
  },
})
const msgError = ref()
const _menu = ref({})
const showModalDelete = ref(false)
const countId = ref(0)

const sections = computed(() => {
  return [
    {
      section: 'Menu name',
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

function convertObjMenu(menus, menusParent) {
  function recurse(elements) {
    for (let element of elements) {
      let menuChild = menus.filter((el) => el.parent_menu == element.menu_id)
      menuChild.sort((a, b) => a.id - b.id)
      element.elements = menuChild
      if (menuChild && menuChild.length > 0) {
        recurse(menuChild)
      }
    }
  }

  recurse(menusParent)
  return menusParent
}

const menu = createResource({
  url: 'go1_cms.api.menu.get_menu',
  params: {
    name: props.menuId,
  },
  auto: true,
  transform: (data) => {
    // convert menu to object menu edit
    let menus = data.menus.map((el) => ({
      ...el,
      id: el.idx,
      elements: [],
      parent_menu: el.parent_menu ? el.parent_menu : null,
    }))
    let menusParent = menus.filter((el) => el.parent_menu == null)
    countId.value = menus.length

    _menu.value = {
      ...data,
      menus: convertObjMenu(menus, menusParent),
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
  if (menu.data) {
    // convert menu to object menu edit
    let menus = menu.data.menus.map((el) => ({
      ...el,
      id: el.idx,
      elements: [],
      parent_menu: el.parent_menu ? el.parent_menu : null,
    }))
    let menusParent = menus.filter((el) => el.parent_menu == null)

    return (
      JSON.stringify({
        ...menu.data,
        menus: convertObjMenu(menus, menusParent),
      }) !== JSON.stringify(_menu.value)
    )
  }
  return JSON.stringify(menu.data) !== JSON.stringify(_menu.value)
})

watch(dirty, (val) => {
  alreadyActions.value = true
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

async function callUpdateDoc() {
  msgError.value = null
  if (JSON.stringify(menu.data) == JSON.stringify(_menu.value)) {
    warningMessage(__('No changes in document'))
    return
  }

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
    const doc = await call('go1_cms.api.menu.update_menu', {
      data: {
        ...menuUpdate,
      },
    })
    if (doc.name) {
      createToast({
        title: __('Saved'),
        icon: 'check',
        iconClasses: 'text-green-600',
      })
      menu.reload()
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
    await call('go1_cms.api.menu.delete_menu', {
      name: props.menuId,
    }).then(() => {
      createToast({
        title: __('Deleted'),
        icon: 'check',
        iconClasses: 'text-green-600',
      })
      close()
      router.push({
        name: 'Menu',
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
  () => props.menuId,
  (val) => {
    menu.update({
      params: { name: val },
    })
    menu.reload()
  },
)

// breadcrumbs
const breadcrumbs = computed(() => {
  let items = [{ label: 'Menu', route: { name: 'Menu' } }]
  items.push({
    label: menu.data?.title,
    route: {},
  })
  return items
})
</script>
