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
              <Tooltip
                :text="__('View detail')"
                :hover-delay="1"
                placement="top"
              >
                <div>
                  <Button
                    :variant="'subtle'"
                    theme="blue"
                    size="sm"
                    label=""
                    icon="edit"
                    :route="'/menu/' + item.name"
                  >
                  </Button>
                </div>
              </Tooltip>
              <Tooltip
                :text="__('Delete menu')"
                :hover-delay="1"
                placement="top"
              >
                <div>
                  <Button
                    :variant="'subtle'"
                    theme="red"
                    size="sm"
                    label=""
                    icon="trash"
                    @click="handleShowModalDelete(item)"
                  >
                  </Button>
                </div>
              </Tooltip>
            </div>
          </div>
          <div
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
            <Tooltip :text="item" :hover-delay="1" placement="top">
              <div>
                {{ timeAgo(item) }}
              </div>
            </Tooltip>
          </div>
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
          <b>"{{ selectedItem.title }}"</b>?
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
import {
  ListView,
  ListHeader,
  ListRows,
  ListRow,
  ListRowItem,
  ListFooter,
  call,
  Tooltip,
  Dialog,
} from 'frappe-ui'
import { createToast, errorMessage } from '@/utils'
import { ref, watch } from 'vue'
import { globalStore } from '@/stores/global'
import { timeAgo } from '@/utils'

const { changeLoadingValue, $dialog } = globalStore()
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
const showModalDelete = ref(false)
const selectedItem = ref()

watch(pageLengthCount, (val, old_value) => {
  if (val === old_value) return
  emit('updatePageCount', val)
})

// delete
function handleShowModalDelete(item) {
  selectedItem.value = item
  showModalDelete.value = true
}

async function deleteDoc(close) {
  changeLoadingValue(true, __('Deleting...'))
  try {
    await call('go1_cms.api.menu.delete_menu', {
      name: selectedItem.value?.name,
    }).then(() => {
      createToast({
        title: __('Deleted'),
        icon: 'check',
        iconClasses: 'text-green-600',
      })
      list.value.reload()
      close()
    })
  } catch (err) {
    if (err.messages && err.messages.length) {
      errorMessage(__('An error has occurred'), err.messages.join(', '))
    }
  }
  changeLoadingValue(false)
}
</script>
