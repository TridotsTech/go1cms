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
    <ListHeader class="mx-5" @columnWidthUpdated="emit('columnWidthUpdated')" />
    <ListRows id="list-rows">
      <ListRow
        class="mx-5"
        v-for="row in rows"
        :key="row.name"
        v-slot="{ idx, column, item }"
        :row="row"
      >
        <ListRowItem
          :item="item"
          @click="(event) => emit('applyFilter', { event, idx, column, item })"
        >
          <template #prefix>
            <div v-if="column.key === 'action'">
              <div class="flex align-middle gap-4">
                <Tooltip text="Xem" :hover-delay="1" :placement="'top'">
                  <Button
                    :variant="'subtle'"
                    theme="blue"
                    size="sm"
                    label=""
                    icon="eye"
                  >
                  </Button>
                </Tooltip>
                <Dropdown
                  :options="[
                    {
                      group: 'Cấu hình',
                      items: [
                        {
                          label: 'Đặt chỉnh sửa',
                          icon: 'edit',
                        },
                        {
                          label: 'Đặt phát hành',
                          icon: 'globe',
                        },
                      ],
                    },
                    {
                      group: 'Xóa',
                      items: [
                        {
                          label: 'Xóa giao diện',
                          icon: 'trash',
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
              <span v-if="item.edit === 1">Đã đặt</span>
              <span v-else>Chưa đặt</span>
            </div>
            <div v-else-if="column.key === 'published'">
              <span v-if="item.published === 1">Đã phát hành</span>
              <span v-else>Chưa phát hành</span>
            </div>
          </template>
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
} from 'frappe-ui'
import { createToast } from '@/utils'
import { globalStore } from '@/stores/global'
import { onMounted, ref, watch } from 'vue'
import { useRouter } from 'vue-router'

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

watch(pageLengthCount, (val, old_value) => {
  if (val === old_value) return
  emit('updatePageCount', val)
})
</script>
