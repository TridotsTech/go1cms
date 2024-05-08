<template>
  <ListView
    :class="$attrs.class"
    :columns="columns"
    :rows="rows"
    :options="{
      selectable: options.selectable,
      showTooltip: options.showTooltip,
      resizeColumn: options.resizeColumn,
      emptyState: options.emptyState,
    }"
    row-key="name"
  >
    <ListHeader @columnWidthUpdated="emit('columnWidthUpdated')" />
    <div
      class="flex relative justify-center items-center min-h-[250px]"
      v-if="loading"
    >
      <div
        class="absolute w-full h-full rounded-md opacity-80 bg-gray-200"
      ></div>
      <LoadingIndicator class="h-6 w-6" />
    </div>
    <ListRows id="list-rows" v-else-if="rows && rows.length">
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
          <div v-if="column.key === 'action'">
            <div class="flex align-middle gap-4">
              <Tooltip text="Xem" :hover-delay="1" :placement="'top'">
                <Button
                  :variant="'subtle'"
                  theme="blue"
                  size="sm"
                  label=""
                  icon="eye"
                  :link="item.route_web"
                >
                </Button>
              </Tooltip>
              <Dropdown
                :options="[
                  {
                    group: 'Cấu hình',
                    items: [
                      {
                        label: 'Đổi tên',
                        icon: 'edit-3',
                        onClick: () => editValues(item),
                      },
                      {
                        label: 'Đặt là website chính',
                        icon: 'key',
                        onClick: () => setPrimaryMyWebsite(item),
                      },
                      {
                        label: 'Đặt là website chỉnh sửa',
                        icon: 'edit',
                        onClick: () => setEditMyWebsite(item),
                      },
                      {
                        label:
                          item.published === 0 ? 'Kích hoạt' : 'Dừng kích hoạt',
                        icon: 'globe',
                        onClick: () => setPublishedMyWebsite(item),
                      },
                    ],
                  },
                  {
                    group: 'Xóa',
                    items: [
                      {
                        label: 'Xóa website',
                        icon: 'trash',
                        onClick: () => deleteMyWebsite(item),
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
                Đã kích hoạt
              </Badge>
            </span>
            <span v-else>
              <Badge :variant="'outline'" theme="gray" size="sm" label="Badge">
                Chưa kịch hoạt
              </Badge>
            </span>
          </div>
          <div v-else-if="column.key === 'status_web'">
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
          <div v-else-if="column.type === 'Check'">
            <FormControl
              type="checkbox"
              :modelValue="item"
              :disabled="true"
              class="text-gray-900"
            />
          </div>
        </ListRowItem>
      </ListRow>
    </ListRows>
    <ListEmptyState class="min-h-[250px]" v-else></ListEmptyState>
  </ListView>
  <ListFooter
    v-if="pageLengthCount"
    class="border-t px-5 py-2"
    v-model="pageLengthCount"
    :options="{
      rowCount: options.rowCount,
      totalCount: options.totalCount,
    }"
    @loadMore="emit('loadMore')"
  />
  <Dialog v-model="showDialog">
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
        <Button class="ml-2" @click="showDialog = false"> Đóng </Button>
        <Button variant="solid" theme="blue" @click="changeNameWebsite">
          Xác nhận
        </Button>
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
  ListEmptyState,
  Dropdown,
  call,
  Tooltip,
  Dialog,
  ErrorMessage,
} from 'frappe-ui'
import { createToast, errorMessage } from '@/utils'
import { onMounted, ref, watch } from 'vue'
import { globalStore } from '@/stores/global'
import LoadingIndicator from '@/components/Icons/LoadingIndicator.vue'

const { changeLoadingValue, $dialog, changeNameWebsiteEdit } = globalStore()
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
  'loading',
  'reFresh',
  'loadMore',
  'updatePageCount',
  'columnWidthUpdated',
  'applyFilter',
])

const loading = defineModel('loading')
const pageLengthCount = defineModel()

watch(pageLengthCount, (val, old_value) => {
  if (val === old_value) return
  emit('updatePageCount', val)
})
const showDialog = ref(false)
const itemSelected = ref({})
const errorTextMessage = ref({ name_web: null })
const inputValues = { name_web: '' }

// change name web
function editValues(item) {
  inputValues.name_web = item.name_web
  errorTextMessage.value = { name_web: null }
  itemSelected.value = item
  showDialog.value = true
}

async function changeNameWebsite() {
  if (!inputValues.name_web) {
    errorTextMessage.value.name_web = 'Tên website được để trống'
    return false
  }

  if (inputValues.name_web === itemSelected.value.name_web) {
    errorTextMessage.value.name_web = 'Tên mới không thể trùng với tên cũ'
    return false
  }
  errorTextMessage.value.name_web = ''

  changeLoadingValue(true, 'Đang cập nhật...')
  try {
    await call('go1_cms.api.client_website.change_name_web_client_website', {
      name: itemSelected.value.id,
      name_web: inputValues.name_web,
    }).then(() => {
      createToast({
        title: 'Thành công',
        icon: 'check',
        iconClasses: 'text-green-600',
      })

      if (itemSelected.value.edit == 1) {
        changeNameWebsiteEdit(inputValues.name_web)
      }

      changeLoadingValue(false)
      emit('reFresh')
      showDialog.value = false
    })
  } catch (err) {
    changeLoadingValue(false)
    if (err.messages && err.messages.length) {
      errorMessage('Có lỗi xảy ra', err.messages[0])
    }
  }
}

// set primary
function setPrimaryMyWebsite(item) {
  $dialog({
    title: 'Đặt website là bản chính',
    message: `Bạn chắc chắn muốn đặt website có tên "${item.name_web}" là website hoạt động chính?`,
    variant: 'danger',
    actions: [
      {
        label: 'Đặt website là website chính',
        variant: 'solid',
        theme: 'blue',
        onClick: async (close) => {
          if (item.status_web == 'Bản chính') {
            createToast({
              title: 'Không thể chuyển đổi',
              text: 'Website đã đặt là website chính',
              icon: 'alert-circle',
              iconClasses: 'text-orange-600',
            })
            return false
          }

          changeLoadingValue(true, 'Đang đặt...')
          try {
            await call(
              'go1_cms.api.client_website.set_primary_client_website',
              {
                name: item.id,
              }
            ).then(() => {
              createToast({
                title: 'Thành công',
                icon: 'check',
                iconClasses: 'text-green-600',
              })
              changeLoadingValue(false)
              emit('reFresh')
              close()
            })
          } catch (err) {
            changeLoadingValue(false)
            if (err.messages && err.messages.length) {
              errorMessage('Có lỗi xảy ra', err.messages[0])
            }
          }
        },
      },
    ],
  })
}

// set edit
function setEditMyWebsite(item) {
  $dialog({
    title: 'Đặt website chỉnh sửa',
    message: `Bạn chắc chắn muốn đặt website có tên "${item.name_web}" cho việc chỉnh sửa?`,
    variant: 'danger',
    actions: [
      {
        label: 'Đặt website chỉnh sửa',
        variant: 'solid',
        theme: 'blue',
        onClick: async (close) => {
          if (item.edit == 1) {
            createToast({
              title: 'Không thể chuyển đổi',
              text: 'Website đã đặt là chỉnh sửa',
              icon: 'alert-circle',
              iconClasses: 'text-orange-600',
            })
            return false
          }

          changeLoadingValue(true, 'Đang đặt...')
          try {
            await call(
              'go1_cms.api.client_website.update_edit_client_website',
              {
                name: item.id,
              }
            ).then(() => {
              createToast({
                title: 'Thành công',
                icon: 'check',
                iconClasses: 'text-green-600',
              })
              // emit('reFresh')
              // close()
              // changeLoadingValue(false)
              window.location.reload()
            })
          } catch (err) {
            changeLoadingValue(false)
            if (err.messages && err.messages.length) {
              errorMessage('Có lỗi xảy ra', err.messages[0])
            }
          }
        },
      },
    ],
  })
}

// set published
function setPublishedMyWebsite(item) {
  let title = 'kích hoạt website'
  let message = `Bạn chắc chắn muốn kích hoạt website có tên "${item.name_web}"?`
  let loadingText = 'Đang kích hoạt website...'
  if (item.published == 1) {
    title = 'Dứng kích hoạt website'
    message = `Bạn chắc chắn muốn dừng kích hoạt website có tên "${item.name_web}"?`
    loadingText = 'Đang dừng kích hoạt website...'
  }

  $dialog({
    title: title,
    message: message,
    variant: 'danger',
    actions: [
      {
        label: title,
        variant: 'solid',
        theme: 'red',
        onClick: async (close) => {
          changeLoadingValue(true, loadingText)
          try {
            await call(
              'go1_cms.api.client_website.update_published_client_website',
              {
                name: item.id,
                published: item.published == 1 ? 0 : 1,
              }
            ).then(() => {
              createToast({
                title: 'Thành công',
                icon: 'check',
                iconClasses: 'text-green-600',
              })
              emit('reFresh')
              close()
              changeLoadingValue(false)
            })
          } catch (err) {
            changeLoadingValue(false)
            if (err.messages && err.messages.length) {
              errorMessage('Có lỗi xảy ra', err.messages[0])
            }
          }
        },
      },
    ],
  })
}

// delete
function deleteMyWebsite(item) {
  $dialog({
    title: 'Xóa website',
    message: `Bạn chắc chắn muốn xóa website có tên: ${item.name_web}?`,
    variant: 'danger',
    actions: [
      {
        label: 'Xóa',
        variant: 'solid',
        theme: 'red',
        onClick: async (close) => {
          changeLoadingValue(true, 'Đang xóa...')
          try {
            await call('go1_cms.api.client_website.delete_client_website', {
              name: item.id,
            }).then(() => {
              createToast({
                title: 'Xóa thành công',
                icon: 'check',
                iconClasses: 'text-green-600',
              })
              emit('reFresh')
              close()
              changeLoadingValue(false)
              if (item.edit == 1) {
                window.location.reload()
              }
            })
          } catch (err) {
            changeLoadingValue(false)
            if (err.messages && err.messages.length) {
              errorMessage('Có lỗi xảy ra', err.messages[0])
            }
          }
        },
      },
    ],
  })
}
</script>
