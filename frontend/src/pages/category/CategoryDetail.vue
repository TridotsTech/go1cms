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
              group: 'Xóa',
              items: [
                {
                  label: 'Xóa danh mục',
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
          label="Hủy"
          @click="category.reload()"
          :disabled="!dirty"
        ></Button>
        <Button
          variant="solid"
          theme="blue"
          size="md"
          label="Lưu"
          @click="callUpdateDoc"
          :disabled="!dirty"
        ></Button>
      </div>
    </template>
  </LayoutHeader>
  <div class="p-6 overflow-auto">
    <div v-if="msgError" class="p-4 border border-gray-300 rounded-sm mb-4">
      <div class="text-base text-red-600 font-bold mb-2">Có lỗi xảy ra:</div>
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
      title: 'Xóa danh mục',
      actions: [
        {
          label: 'Xóa',
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
          Bạn chắc chắn muốn xóa danh mục:
          <b>"{{ _category?.category_title }}"</b>?
        </div>
        <div class="text-base">
          <p>
            - Điều này sẽ
            <b class="text-red-600">xóa toàn bộ các bài viết</b>
            liên quan đến danh mục này.
          </p>
          <p>- <b class="text-red-600">Không thể hoàn tác</b>.</p>
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
import { createToast, errorMessage, warningMessage } from '@/utils'
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
          label: 'Tên danh mục',
          mandatory: true,
          name: 'category_title',
          type: 'data',
          placeholder: 'Nhập tên danh mục',
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
          label: 'Mô tả',
          name: 'description',
          type: 'textarea',
          placeholder: 'Nhập mô tả',
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
    msgError.value = `Tên danh mục không được phép chứa các ký tự đặc biệt: [&\/\\#+()$~%.\`'":*?<>{}]`
    return false
  }

  changeLoadingValue(true, 'Đang lưu...')
  try {
    const doc = await call('go1_cms.api.category.update_category', {
      data: {
        ..._category.value,
      },
    })
    if (doc.name) {
      createToast({
        title: 'Cập nhật thành công',
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
    if (err.messages && err.messages.length) {
      msgError.value = err.messages.join(', ')
      errorMessage('Có lỗi xảy ra', err.messages.join(', '))
    } else {
      errorMessage('Có lỗi xảy ra', err)
    }
  }
  changeLoadingValue(false)
}

async function deleteDoc(close) {
  changeLoadingValue(true, 'Đang xóa...')
  try {
    await call('go1_cms.api.category.delete_category', {
      name: props.categoryId,
    }).then(() => {
      createToast({
        title: 'Xóa thành công',
        icon: 'check',
        iconClasses: 'text-green-600',
      })
      close()
      router.push({
        name: 'Categories',
      })
    })
  } catch (err) {
    if (err.messages && err.messages.length) {
      msgError.value = err.messages.join(', ')
      errorMessage('Có lỗi xảy ra', err.messages.join(', '))
    } else {
      errorMessage('Có lỗi xảy ra', err)
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
  let items = [{ label: 'Quản lý danh mục', route: { name: 'Categories' } }]
  items.push({
    label: category.data?.name,
    route: {},
  })
  return items
})
</script>
