<style scoped>
.flip-list-move {
  transition: transform 0.5s;
}

.no-move {
  transition: transform 0s;
}
</style>

<template>
  <Draggable
    v-bind="dragOptions"
    tag="div"
    class="item-container border p-1 my-1"
    :list="list"
    :value="value"
    item-key="idx"
    handle=".handle"
    @change="$emit('change')"
  >
    <template #item="{ element, index }">
      <div class="item-group mb-1">
        <div
          class="p-2 py-1 border rounded-sm flex flex-wrap gap-4 bg-gray-200 items-center"
        >
          <div class="flex gap-2 items-center">
            <MenuIcon class="h-6 text-gray-700 cursor-move handle" />
            <span class="text-base">
              {{ element.menu_label }}
            </span>
          </div>
          <div class="flex gap-1 items-center">
            <Tooltip text="Chỉnh sửa" :hover-delay="1" :placement="'top'">
              <span>
                <Button
                  variant="ghost"
                  class="btn btn-secondary"
                  theme="blue"
                  icon="edit-3"
                  @click="
                    $emit('updateItem', {
                      id: element.id,
                      menu_label: element.menu_label,
                      redirect_url: element.redirect_url,
                      action: 'edit',
                    })
                  "
                >
                </Button>
              </span>
            </Tooltip>
            <Tooltip text="Xóa" :hover-delay="1" :placement="'top'">
              <span>
                <Button
                  variant="ghost"
                  class="btn btn-secondary"
                  theme="red"
                  icon="trash-2"
                  @click="
                    $emit('updateItem', {
                      id: element.id,
                      action: 'delete',
                    })
                  "
                >
                </Button>
              </span>
            </Tooltip>
          </div>
        </div>
        <nested
          v-if="maxLevel - 1 > 0"
          :maxLevel="maxLevel - 1"
          class="item-sub ml-6"
          :list="element.elements"
          :parentId="element.id"
          item-key="idx"
          @change="$emit('change')"
          @updateItem="(val) => $emit('updateItem', val)"
        />
      </div>
    </template>
    <template #footer role="group" aria-label="Basic example" key="footer">
      <Tooltip text="Thêm" :hover-delay="1" :placement="'top'">
        <span>
          <Button
            variant="ghost"
            class="btn btn-secondary"
            icon="plus-circle"
            @click="
              $emit('updateItem', { id: parentId, value: '', action: 'add' })
            "
          >
          </Button>
        </span>
      </Tooltip>
    </template>
  </Draggable>
</template>

<script>
import Draggable from 'vuedraggable'
import MenuIcon from '@/components/Icons/MenuIcon.vue'

export default {
  name: 'nested',
  methods: {},
  components: {
    Draggable,
    MenuIcon,
  },
  emits: ['change', 'updateItem'],
  computed: {
    dragOptions() {
      return {
        animation: 0,
        group: 'description',
        disabled: false,
        ghostClass: 'ghost',
      }
    },
  },
  props: {
    value: {
      required: false,
      type: Array,
      default: null,
    },
    list: {
      required: false,
      type: Array,
      default: null,
    },
    parentId: {
      type: [String, Number],
      default: null,
    },
    maxLevel: {
      type: Number,
      default: 3,
    },
  },
}
</script>
