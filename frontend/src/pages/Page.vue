<template>
  <LayoutHeader>
    <template #left-header>
      <Breadcrumbs :items="breadcrumbs" />
    </template>
    <template #right-header>
      <div
        class="gap-2 justify-end"
        :class="alreadyActions ? 'flex' : 'hidden'"
      >
        <Dropdown
          v-if="_page?.web_page?.allow_delete"
          :options="[
            {
              group: 'Xóa',
              items: [
                {
                  label: 'Xóa trang',
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
          :disabled="!dirty"
          @click="cacelSaveDoc"
        ></Button>
        <Button
          :variant="'solid'"
          theme="blue"
          size="md"
          label="Lưu"
          :disabled="!dirty"
          @click="callUpdateDoc"
        >
        </Button>
      </div>
    </template>
  </LayoutHeader>
  <div ref="refToTop" class="p-6 overflow-auto">
    <div v-if="msgError" class="p-4 border border-gray-300 rounded-sm mb-4">
      <div class="text-base text-red-600 font-bold mb-2">Có lỗi xảy ra:</div>
      <ErrorMessage :message="msgError" />
    </div>
    <FieldsComponent v-model="_page"></FieldsComponent>
    <FieldsSectionComponent v-model="_page"></FieldsSectionComponent>
  </div>
  <Dialog
    :options="{
      title: 'Xóa trang',
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
          Bạn chắc chắn muốn xóa trang:
          <b>"{{ _page?.web_page?.name_page }}"</b>?
        </div>
        <div class="text-base">
          <p>- <b class="text-red-600">Không thể hoàn tác</b>.</p>
        </div>
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
  Dropdown,
} from 'frappe-ui'
import { ref, computed, watch } from 'vue'
import { useRoute } from 'vue-router'
import {
  createToast,
  errorMessage,
  handleUploadFieldImage,
  scrollToTop,
} from '@/utils'
import { globalStore } from '@/stores/global'

const { changeLoadingValue } = globalStore()
const route = useRoute()

const _page = ref({})
const msgError = ref()
const refToTop = ref(null)

// get detail
const page = createResource({
  url: 'go1_cms.api.page.get_info_page',
  method: 'GET',
  params: { name: route.query.view },
  auto: true,
  transform: (data) => {
    _page.value = JSON.parse(JSON.stringify(data))
    return data
  },
})

watch(route, (val, oldVal) => {
  page.update({
    params: { name: route.query.view },
  })
  page.reload()
  scrollToTop(refToTop)
})

// handle allow actions
const alreadyActions = ref(false)
const dirty = computed(() => {
  return JSON.stringify(page.data) !== JSON.stringify(_page.value)
})

watch(dirty, (val) => {
  alreadyActions.value = true
})

const breadcrumbs = computed(() => {
  let items = []
  items.push({
    label: page.data?.web_page.name_page,
    route: {
      name: 'Page',
      query: { view: route.query.view },
    },
  })
  return items
})

async function callUpdateDoc() {
  changeLoadingValue(true, 'Đang lưu...')
  try {
    let data = JSON.parse(JSON.stringify(_page.value))
    // upload image
    await handleUploadFieldImage(
      data,
      _page,
      'Web Page Builder',
      _page.value?.web_page?.doc_page,
    )

    let docUpdate = await call('go1_cms.api.page.update_info_page', {
      data: data,
    })

    if (docUpdate.name) {
      page.reload()

      createToast({
        title: 'Cập nhật thành công',
        icon: 'check',
        iconClasses: 'text-green-600',
      })
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

async function cacelSaveDoc() {
  await page.reload()
}

// delete page
const showModalDelete = ref(false)
async function deleteDoc(close) {
  changeLoadingValue(true, 'Đang xóa...')
  try {
    await call('go1_cms.api.page.delete_page', {
      name: route.query.view,
    }).then(() => {
      createToast({
        title: 'Xóa thành công',
        icon: 'check',
        iconClasses: 'text-green-600',
      })
      close()
      window.location.href = '/cms/my-website'
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
</script>
