<template>
  <LayoutHeader>
    <template #left-header>
      <Breadcrumbs :items="breadcrumbs" />
    </template>
  </LayoutHeader>
  <div class="p-6 mt-12">
    <div class="border-b mb-4 pb-2 border-gray-300">
      <div class="flex flex-wrap justify-between items-center gap-2">
        <h2 class="font-bold text-3xl">Cập nhật danh mục bài viết</h2>
        <div class="flex rounded-sm gap-2 justify-end">
          <Button
            variant="subtle"
            theme="gray"
            size="md"
            label="Hủy"
            route="/category"
          ></Button>
          <Button
            variant="solid"
            theme="blue"
            size="md"
            label="Lưu"
            @click="callUpdateDoc"
          ></Button>
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
        </div>
      </div>
    </div>
    <div v-if="_category" class="p-4 border border-gray-300 rounded-sm mb-4">
      <div class="mb-5">
        <Fields :sections="sections" :data="_category" />
      </div>
      <div class="border-t border-gray-300">
        <ErrorMessage class="mt-3" :message="msgError" />
        <div class="flex py-4 gap-2 justify-end">
          <Button
            :variant="'subtle'"
            theme="gray"
            size="md"
            label="Hủy"
            route="/category"
          ></Button>
          <Button
            variant="solid"
            theme="blue"
            size="md"
            label="Lưu"
            @click="callUpdateDoc"
          ></Button>
        </div>
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
import { ref, computed, watch, nextTick } from 'vue'
import { createToast, errorMessage } from '@/utils'
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

const breadcrumbs = [
  { label: 'Quản lý danh mục', route: { name: 'Category' } },
  { label: 'Cập nhật danh mục bài viết', route: {} },
]

const sections = computed(() => {
  return [
    {
      section: 'Category Name',
      columns: 1,
      class: 'md:grid-cols-2',
      fields: [
        {
          label: 'Tên danh mục',
          mandatory: true,
          name: 'category_title',
          type: 'data',
          placeholder: 'Nhập tên danh mục',
          doctype: 'Mbw Blog Category',
        },
      ],
    },
    {
      section: 'Description',
      columns: 2,
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
  cache: ['category', props.categoryId],
  params: {
    name: props.categoryId,
  },
  auto: true,
  transform: (data) => {
    return data
  },
})

watch(category, (val) => {
  nextTick(() => {
    _category.value = {
      ...category.data,
    }
  })
})

async function callUpdateDoc() {
  changeLoadingValue(true, 'Đang lưu...')
  try {
    const doc = await call('go1_cms.api.category.update_category', {
      data: {
        ..._category.value,
      },
    })
    createToast({
      title: 'Cập nhật thành công',
      icon: 'check',
      iconClasses: 'text-green-600',
    })
  } catch (err) {
    msgError.value = err.messages.join(', ')
    errorMessage('Có lỗi xảy ra', err.messages.join(', '))
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
        name: 'Category',
      })
    })
  } catch (err) {
    if (err.messages && err.messages.length) {
      errorMessage('Có lỗi xảy ra', err.messages.join(', '))
    }
  }
  changeLoadingValue(false)
}
</script>
