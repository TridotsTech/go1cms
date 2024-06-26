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
          :options="[
            {
              group: 'Xóa',
              items: [
                {
                  label: 'Xóa liên hệ',
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
          @click="contact.reload()"
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
    <div v-if="_contact" class="p-4 border border-gray-300 rounded-sm mb-4">
      <div class="mb-5">
        <Fields :sections="sections" :data="_contact" />
      </div>
    </div>
  </div>
  <Dialog
    :options="{
      title: 'Xóa liên hệ',
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
          Bạn chắc chắn muốn xóa liên hệ:
          <b>"{{ _contact?.email }}"</b>?
        </div>
        <div class="text-base">
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
  contactId: {
    type: String,
    required: true,
  },
})
const msgError = ref()
const _contact = ref({})
const showModalDelete = ref(false)

const sections = computed(() => {
  return [
    {
      section: 'Section 1',
      columns: 1,
      class: 'md:grid-cols-2',
      fields: [
        {
          label: 'Họ',
          mandatory: false,
          name: 'last_name',
          type: 'data',
          placeholder: 'Nhập tên họ',
        },
        {
          label: 'Tên',
          mandatory: false,
          name: 'first_name',
          type: 'data',
          placeholder: 'Nhập tên',
        },
        {
          label: 'Họ và tên',
          mandatory: false,
          name: 'full_name',
          type: 'data',
          placeholder: 'Nhập họ và tên',
        },
        {
          label: 'Email',
          mandatory: false,
          name: 'email',
          type: 'data',
          placeholder: 'Nhập email',
        },
        {
          label: 'Số điện thoại',
          mandatory: false,
          name: 'phone_number',
          type: 'data',
          placeholder: 'Nhập số điện thoại',
        },
      ],
    },
    {
      section: 'Section 2',
      columns: 1,
      class: 'md:grid-cols-2',
      hideBorder: true,
      fields: [
        {
          label: 'Thông tin thêm',
          name: 'message',
          type: 'textarea',
          placeholder: 'Nhập thông tin',
          rows: 10,
        },
        {
          label: 'Nguồn',
          name: 'source',
          type: 'textarea',
          placeholder: 'Nhập nguồn',
          rows: 10,
        },
        {
          label: 'UTM Source',
          mandatory: false,
          name: 'utm_source',
          type: 'data',
          placeholder: 'Nhập utm source',
        },
        {
          label: 'Utm Campaign',
          mandatory: false,
          name: 'utm_campaign',
          type: 'data',
          placeholder: 'Nhập utm campaign',
        },
      ],
    },
  ]
})

const contact = createResource({
  url: 'go1_cms.api.mbw_contact.get_contact',
  params: {
    name: props.contactId,
  },
  auto: true,
  transform: (data) => {
    _contact.value = {
      ...data,
    }
    return data
  },
})

// handle allow actions
const alreadyActions = ref(false)
const dirty = computed(() => {
  return JSON.stringify(contact.data) !== JSON.stringify(_contact.value)
})

watch(dirty, (val) => {
  alreadyActions.value = true
})

async function callUpdateDoc() {
  msgError.value = null

  if (JSON.stringify(contact.data) == JSON.stringify(_contact.value)) {
    warningMessage('Tài liệu không thay đổi')
    return
  }

  changeLoadingValue(true, 'Đang lưu...')
  try {
    const doc = await call('go1_cms.api.mbw_contact.update_contact', {
      data: {
        ..._contact.value,
      },
    })
    if (doc.name) {
      createToast({
        title: 'Cập nhật thành công',
        icon: 'check',
        iconClasses: 'text-green-600',
      })
      contact.reload()
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
    await call('go1_cms.api.mbw_contact.delete_contact', {
      name: props.contactId,
    }).then(() => {
      createToast({
        title: 'Xóa thành công',
        icon: 'check',
        iconClasses: 'text-green-600',
      })
      close()
      router.push({
        name: 'Contacts',
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
  () => props.contactId,
  (val) => {
    contact.update({
      params: { name: val },
    })
    contact.reload()
  },
)

// breadcrumbs
const breadcrumbs = computed(() => {
  let items = [{ label: 'Danh sách liên hệ', route: { name: 'Contacts' } }]
  items.push({
    label: contact.data?.email,
    route: {},
  })
  return items
})
</script>
