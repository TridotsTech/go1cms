<template>
  <ListView
    :class="$attrs.class"
    :columns="columns"
    :rows="rows"
    :options="{
      selectable: options.selectable,
      showTooltip: options.showTooltip,
      resizeColumn: options.resizeColumn,
    }"
    row-key="name"
  >
    <ListHeader @columnWidthUpdated="emit('columnWidthUpdated')" />
    <ListRows id="list-rows" v-if="rows && rows.length">
      <ListRow
        v-for="row in rows"
        :key="row.name_web"
        v-slot="{ idx, column, item }"
        :row="row"
      >
        <ListRowItem
          :item="item"
          @click="(event) => emit('applyFilter', { event, idx, column, item })"
        >
          <template #prefix> </template>
          <div v-if="column.key === 'action_button'">
            <div class="flex align-middle gap-4">
              <Tooltip text="Xem" :hover-delay="1" :placement="'top'">
                <div>
                  <Button
                    :variant="'subtle'"
                    theme="blue"
                    size="sm"
                    label=""
                    icon="eye"
                    :link="item.route_web"
                  >
                  </Button>
                </div>
              </Tooltip>
              <Dropdown
                :options="[
                  {
                    group: 'Cấu hình',
                    items: [
                      {
                        label: 'Đổi tên',
                        icon: 'edit-3',
                        onClick: () => handleShowModal(item),
                      },
                      {
                        label: 'Đặt là website chính',
                        icon: 'key',
                        onClick: () => handleShowDialog(item, 'set primary'),
                      },
                      {
                        label: 'Đặt là website chỉnh sửa',
                        icon: 'edit',
                        onClick: () => handleShowDialog(item, 'set edit'),
                      },
                      {
                        label:
                          item.published === 0 ? 'Kích hoạt' : 'Dừng kích hoạt',
                        icon: 'globe',
                        onClick: () => handleShowDialog(item, 'set publish'),
                      },
                    ],
                  },
                  {
                    group: __('Delete'),
                    items: [
                      {
                        label: 'Xóa website',
                        icon: 'trash',
                        onClick: () => handleShowDialog(item, 'delete'),
                      },
                    ],
                  },
                ]"
              >
                <Button>
                  <template #icon>
                    <FeatherIcon name="more-horizontal" class="h-4 w-4" />
                  </template>
                </Button>
              </Dropdown>
            </div>
          </div>
          <div v-else-if="column.key === 'edit'">
            <Badge
              v-if="item === 1"
              :variant="'outline'"
              theme="green"
              size="sm"
              label="Badge"
            >
              Đang đặt
            </Badge>

            <!-- <Badge
              v-else
              :variant="'outline'"
              theme="gray"
              size="sm"
              label="Badge"
            >
              Chưa đặt
            </Badge> -->
          </div>
          <div v-else-if="column.key === 'published'">
            <span v-if="item === 1">
              <Badge :variant="'outline'" theme="green" size="sm" label="Badge">
                Đang kích hoạt
              </Badge>
            </span>
            <span v-else>
              <Badge :variant="'outline'" theme="gray" size="sm" label="Badge">
                Chưa kích hoạt
              </Badge>
            </span>
          </div>
          <div v-else-if="column.key === 'type_web'">
            <span v-if="item === 'Bản chính'" class="text-blue-600 text-base">
              {{ item }}
            </span>
            <span v-else class="text-base">
              {{ item }}
            </span>
          </div>
          <Tooltip
            :text="item.label"
            v-if="
              [
                'modified',
                'creation',
                'first_response_time',
                'first_responded_on',
                'response_by',
              ].includes(column.key)
            "
            class="truncate text-base"
          >
            {{ item.timeAgo }}
          </Tooltip>
          <div
            v-else-if="column.key === 'sla_status'"
            class="truncate text-base"
          >
            <Badge
              v-if="item.value"
              :variant="'subtle'"
              :theme="item.color"
              size="md"
              :label="item.value"
            />
          </div>
          <!-- <div v-else-if="column.type === 'Check'">
            <FormControl
              type="checkbox"
              :modelValue="item"
              :disabled="true"
              class="text-gray-900"
            />
          </div> -->
        </ListRowItem>
      </ListRow>
    </ListRows>
  </ListView>
  <ListFooter
    v-if="pageLengthCount"
    class="border-t py-2"
    v-model="pageLengthCount"
    :options="{
      rowCount: options.rowCount,
      totalCount: options.totalCount,
    }"
    @loadMore="emit('loadMore')"
  />

  <!-- modal edit name -->
  <Dialog v-model="showModalEditName">
    <template #body-title>
      <h3>Đổi tên website</h3>
    </template>
    <template #body-content>
      <FormControl
        :type="'text'"
        size="sm"
        variant="subtle"
        placeholder=""
        :disabled="false"
        label="Tên website mới"
        v-model="inputValues.name_web"
      />
      <ErrorMessage class="my-2" :message="errorTextMessage.name_web" />
    </template>
    <template #actions>
      <div class="flex justify-end gap-4">
        <Button class="ml-2" @click="showModalEditName = false">
          {{ __('Close') }}
        </Button>
        <Button variant="solid" theme="blue" @click="changeNameWebsite">
          {{ __('Confirm') }}
        </Button>
      </div>
    </template>
  </Dialog>
  <!-- dialog delete -->
  <Dialog
    :options="{
      title: 'Xóa website',
      actions: [
        {
          label: __('Delete'),
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
          Bạn chắc chắn muốn xóa website có tên:
          <b>"{{ selectedItem.name_web }}"</b>?
        </div>
        <div class="text-base">
          <p>
            <b class="text-red-600">- {{ __('Cannot be undone.') }}</b>
          </p>
        </div>
      </div>
    </template>
  </Dialog>
  <!-- dialog set edit -->
  <Dialog
    :options="{
      title: 'Đặt website chỉnh sửa',
      actions: [
        {
          label: 'Đặt website chỉnh sửa',
          variant: 'solid',
          theme: 'blue',
          onClick: (close) => setEditMyWebsite(close),
        },
      ],
    }"
    v-model="showDialogSetEdit"
  >
    <template v-slot:body-content>
      <div>
        <div>
          Bạn chắc chắn muốn đặt website có tên
          <b>"{{ selectedItem.name_web }}"</b> cho việc chỉnh sửa?
        </div>
      </div>
    </template>
  </Dialog>
  <!-- dialog set publish -->
  <Dialog
    :options="{
      title: contentDialogPublish.title,
      actions: [
        {
          label: contentDialogPublish.title,
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
        <div v-html="contentDialogPublish.message"></div>
      </div>
    </template>
  </Dialog>
  <!-- dialog set primary -->
  <Dialog
    :options="{
      title: __('Set as main website'),
      actions: [
        {
          label: __('Set as main website'),
          variant: 'solid',
          theme: 'blue',
          onClick: (close) => setPrimaryMyWebsite(close),
        },
      ],
    }"
    v-model="showDialogSetPrimary"
  >
    <template v-slot:body-content>
      <div>
        <div>
          {{ __( `Are you sure you want to set the website named <b>{0}</b> as
          the primary active website?`, [selectedItem.name_web], ) }}
        </div>
      </div>
    </template>
  </Dialog>
</template>

<script setup>
import {
  ListView,
  ListHeader,
  ListRows,
  ListRow,
  ListRowItem,
  ListFooter,
  Dropdown,
  call,
  Tooltip,
  Dialog,
  ErrorMessage,
} from 'frappe-ui'
import { createToast, errorMessage } from '@/utils'
import { ref, watch } from 'vue'
import { globalStore } from '@/stores/global'
import { viewsStore } from '@/stores/views'
const { views } = viewsStore()

const { changeLoadingValue, changeNameWebsiteEdit } = globalStore()
const props = defineProps({
  rows: {
    type: Array,
    required: true,
  },
  columns: {
    type: Array,
    required: true,
  },
  options: {
    type: Object,
    default: () => ({
      selectable: true,
      showTooltip: true,
      resizeColumn: false,
      totalCount: 0,
      rowCount: 0,
    }),
  },
})

const emit = defineEmits([
  'loadMore',
  'updatePageCount',
  'columnWidthUpdated',
  'applyFilter',
])

const pageLengthCount = defineModel()
const list = defineModel('list')
const showModalEditName = ref(false)
const showDialogDelete = ref(false)
const showDialogSetPrimary = ref(false)
const showDialogSetPublish = ref(false)
const showDialogSetEdit = ref(false)
const selectedItem = ref({})
const errorTextMessage = ref({ name_web: null })
const inputValues = { name_web: '' }
const contentDialogPublish = ref({})

watch(pageLengthCount, (val, old_value) => {
  if (val === old_value) return
  emit('updatePageCount', val)
})

// change name web
function handleShowModal(item) {
  inputValues.name_web = item.name_web
  errorTextMessage.value = { name_web: null }
  selectedItem.value = item
  showModalEditName.value = true
}

async function changeNameWebsite() {
  if (!inputValues.name_web) {
    errorTextMessage.value.name_web =
      __('Website name') + ' ' + __('cannot be empty')
    return false
  }

  errorTextMessage.value.name_web = ''
  if (inputValues.name_web === selectedItem.value.name_web) {
    return true
  }

  changeLoadingValue(true, __('Updating...'))
  try {
    await call('go1_cms.api.client_website.change_name_web_client_website', {
      name: selectedItem.value.name,
      name_web: inputValues.name_web,
    }).then(() => {
      createToast({
        title: __('Success'),
        icon: 'check',
        iconClasses: 'text-green-600',
      })

      if (selectedItem.value.edit == 1) {
        changeNameWebsiteEdit(inputValues.name_web)
      }

      list.value.reload()
      showModalEditName.value = false
    })
  } catch (err) {
    if (err.messages && err.messages.length) {
      errorMessage(__('An error has occurred'), err.messages[0])
    } else {
      errorMessage(__('An error has occurred'), err)
    }
  }
  changeLoadingValue(false)
}

// show dialog
function handleShowDialog(item, type_modal) {
  selectedItem.value = item
  if (type_modal == 'delete') {
    showDialogDelete.value = true
  } else if (type_modal == 'set edit') {
    showDialogSetEdit.value = true
  } else if (type_modal == 'set primary') {
    showDialogSetPrimary.value = true
  } else if (type_modal == 'set publish') {
    if (item.published == 1) {
      contentDialogPublish.value = {
        title: __('Deactivate Website'),
        message: `${__('Are you sure you want to deactivate the website named')}:
          <b>"${selectedItem.value.name_web}"</b>?`,
      }
    } else {
      contentDialogPublish.value = {
        title: __('Activate Website'),
        message: `${__('Are you sure you want to activate the website named')}:
          <b>"${selectedItem.value.name_web}"</b>?`,
      }
    }
    showDialogSetPublish.value = true
  }
}

// set primary
async function setPrimaryMyWebsite(close) {
  if (selectedItem.value.type_web == 'Bản chính') {
    createToast({
      title: __('Cannot convert'),
      text: __('The website is set as the main website'),
      icon: 'alert-circle',
      iconClasses: 'text-orange-600',
    })
    return false
  }

  changeLoadingValue(true, __('Configuring...'))
  try {
    await call('go1_cms.api.client_website.set_primary_client_website', {
      name: selectedItem.value?.name,
    }).then(() => {
      createToast({
        title: __('Success'),
        icon: 'check',
        iconClasses: 'text-green-600',
      })
      list.value.reload()
      close()
    })
  } catch (err) {
    if (err.messages && err.messages.length) {
      errorMessage(__('An error has occurred'), err.messages[0])
    } else {
      errorMessage(__('An error has occurred'), err)
    }
  }
  changeLoadingValue(false)
}

// set edit
async function setEditMyWebsite(close) {
  if (selectedItem.value.edit == 1) {
    createToast({
      title: __('Cannot convert'),
      text: __('The website is set to edit mode'),
      icon: 'alert-circle',
      iconClasses: 'text-orange-600',
    })
    return false
  }

  changeLoadingValue(true, __('Configuring...'))
  try {
    await call('go1_cms.api.client_website.update_edit_client_website', {
      name: selectedItem.value?.name,
    }).then(() => {
      createToast({
        title: __('Success'),
        icon: 'check',
        iconClasses: 'text-green-600',
      })
      // list.value.reload()
      close()
      changeLoadingValue(false)
      window.location.reload()
    })
  } catch (err) {
    if (err.messages && err.messages.length) {
      errorMessage(__('An error has occurred'), err.messages[0])
    } else {
      errorMessage(__('An error has occurred'), err)
    }
  }
  changeLoadingValue(false)
}

// set published
async function setPublishedMyWebsite(close) {
  let loadingText = __('Activating website...')
  if (selectedItem.value.published == 1) {
    loadingText = __('Deactivating website...')
  }

  changeLoadingValue(true, loadingText)
  try {
    await call('go1_cms.api.client_website.update_published_client_website', {
      name: selectedItem.value.name,
      published: selectedItem.value.published == 1 ? 0 : 1,
    }).then(() => {
      createToast({
        title: __('Success'),
        icon: 'check',
        iconClasses: 'text-green-600',
      })
      list.value.reload()
      close()
    })
  } catch (err) {
    if (err.messages && err.messages.length) {
      errorMessage(__('An error has occurred'), err.messages[0])
    } else {
      errorMessage(__('An error has occurred'), err)
    }
  }
  changeLoadingValue(false)
}

// delete
async function deleteDoc(close) {
  changeLoadingValue(true, __('Deleting...'))
  try {
    await call('go1_cms.api.client_website.delete_client_website', {
      name: selectedItem.value?.name,
    }).then(() => {
      createToast({
        title: __('Deleted'),
        icon: 'check',
        iconClasses: 'text-green-600',
      })
      close()
      if (selectedItem.value.edit == 1) {
        views.reload()
        setTimeout(() => window.location.reload(), 200)
      } else {
        list.value.reload()
      }
    })
  } catch (err) {
    if (err.messages && err.messages.length) {
      errorMessage(__('An error has occurred'), err.messages.join(', '))
    } else {
      errorMessage(__('An error has occurred'), err)
    }
  }
  changeLoadingValue(false)
}
</script>
