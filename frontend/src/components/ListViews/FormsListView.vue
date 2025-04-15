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
                :placement="'top'"
              >
                <div>
                  <Button
                    :variant="'subtle'"
                    theme="blue"
                    size="sm"
                    label=""
                    icon="edit"
                    :route="'/forms/' + item.name"
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
</template>

<script setup>
import {
  ListView,
  ListHeader,
  ListRows,
  ListRow,
  ListRowItem,
  ListFooter,
  Tooltip,
} from 'frappe-ui'
import { watch } from 'vue'
import { timeAgo } from '@/utils'

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
