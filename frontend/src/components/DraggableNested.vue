<template>
  <div class="justify-content-between row">
    <Nested
      :maxLevel="maxLevel"
      :list="modelValue"
      @change="() => dragChange++"
      @updateItem="
        (val) => {
          editMode = val.action == 'add' ? false : true
          currentItem = val
          msgErr.menu_label = ''
          if (val.action != 'delete') {
            showModal = true
          } else {
            handleDeleteMenu()
          }
        }
      "
    />
  </div>
  <Dialog
    v-model="showModal"
    :options="{
      size: 'xl',
      actions: [
        {
          label: editMode ? 'Cập nhật' : 'Thêm',
          variant: 'solid',
          onClick: () => handleUpdateMenu(),
        },
      ],
    }"
  >
    <template #body-title>
      <div class="flex items-center gap-3">
        <h3 class="text-2xl font-semibold leading-6 text-gray-900">
          {{ editMode ? 'Chỉnh sửa' : 'Thêm mới' }}
        </h3>
      </div>
    </template>
    <template #body-content>
      <div class="grid grid-cols-1 gap-4">
        <div>
          <FormControl
            type="autocomplete"
            :options="options_suggest"
            size="sm"
            variant="subtle"
            label="Chọn menu đã có"
            v-model="currentSuggest"
          />
        </div>
        <div>
          <div class="mb-2 text-sm text-gray-600">
            Tên menu
            <span class="text-red-500">*</span>
          </div>
          <FormControl
            type="text"
            :placeholder="__('Nhập tên')"
            v-model="currentItem.menu_label"
          />
        </div>
        <div>
          <div class="mb-2 text-sm text-gray-600">URL chuyển hướng</div>
          <FormControl
            type="text"
            :placeholder="__('Nhập url')"
            v-model="currentItem.redirect_url"
          />
        </div>
        <ErrorMessage :message="msgErr.menu_label" />
      </div>
    </template>
  </Dialog>
</template>

<script>
import Nested from '@/components/nested/nested.vue'
import { call } from 'frappe-ui'

export default {
  name: 'draggable-nested',
  display: 'Draggable Nested',
  props: ['modelValue', 'maxLevel', 'countId'],
  emits: ['update:modelValue', 'update:countId'],
  components: {
    Nested,
  },
  data() {
    return {
      dragChange: 0,
      editMode: false,
      showModal: false,
      currentItem: {},
      msgErr: {},
      options_suggest: [],
      currentSuggest: null,
    }
  },
  watch: {
    showModal(val) {
      if (val) {
        this.currentSuggest = null
      }
    },
    currentSuggest(val) {
      if (val) {
        this.currentItem = {
          ...this.currentItem,
          menu_label: val.label,
          redirect_url: val.value,
        }
      }
    },
    dragChange(val) {
      this.$emit('update:modelValue', this.validMenu(this.modelValue))
    },
  },

  mounted() {
    this.optionsSuggest()
  },
  methods: {
    async optionsSuggest() {
      let menu_suggest = await call('go1_cms.api.menu.get_menu_suggest')
      this.options_suggest = menu_suggest.map((el) => ({
        label: el.menu_label,
        value: el.redirect_url,
      }))
    },
    handleUpdateMenu() {
      if (!this.currentItem.menu_label) {
        this.msgErr['menu_label'] = 'Tên menu không được để trống'
        return false
      }
      let newMenus = [...this.modelValue]
      if (this.currentItem.id) {
        this.updateMenuById(
          newMenus,
          this.currentItem.id,
          this.currentItem.action,
          {
            id: this.countId + 1,
            menu_label: this.currentItem.menu_label,
            redirect_url: this.currentItem.redirect_url,
            elements: [],
          },
        )
      } else {
        newMenus.push({
          id: this.countId + 1,
          menu_label: this.currentItem.menu_label,
          redirect_url: this.currentItem.redirect_url,
          elements: [],
        })
      }
      this.$emit('update:countId', this.countId + 1)

      // update value
      this.$emit('update:modelValue', newMenus)
      this.showModal = false
    },
    handleDeleteMenu() {
      let newMenus = [...this.modelValue]

      this.updateMenuById(
        newMenus,
        this.currentItem.id,
        this.currentItem.action,
      )

      // update value
      this.$emit('update:modelValue', newMenus)
    },
    updateMenuById(data, id, action, newMenu = {}) {
      function recurse(elements) {
        for (let i = 0; i < elements.length; i++) {
          if (elements[i].id === id && action == 'delete') {
            // add item child
            let elms = [...elements[i].elements]
            elements.splice(i, 1)
            if (elms.length) {
              elements.push(...elms)
            }
            return true
          } else if (elements[i].id === id) {
            let dataEdit = {}
            if (action == 'add') {
              dataEdit['elements'] = [...elements[i].elements, newMenu]
            } else {
              dataEdit['menu_label'] = newMenu.menu_label
              dataEdit['redirect_url'] = newMenu.redirect_url
            }
            elements[i] = { ...elements[i], ...dataEdit }
            return true
          }
          if (elements[i].elements && elements[i].elements.length > 0) {
            if (recurse(elements[i].elements)) {
              return true
            }
          }
        }
        return false
      }
      recurse(data)
    },
    recurseValidMenu(elements, elmsOutLevel, level) {
      level += 1
      return elements.map((element) => {
        let newEl = { ...element }
        if (newEl.elements && newEl.elements.length > 0) {
          newEl.elements = this.recurseValidMenu(
            newEl.elements,
            elmsOutLevel,
            level,
          )
        }
        if (level > this.maxLevel) {
          if (elmsOutLevel.findIndex((el) => el.id == element.id) == -1) {
            elmsOutLevel.push({ ...element, elements: [] })
          }
        }
        if (level > this.maxLevel - 1) {
          newEl.elements = []
        }
        return newEl
      })
    },

    validMenu(data) {
      let elmsOutLevel = []
      let level = 0

      let newArray = this.recurseValidMenu(data, elmsOutLevel, level)
      newArray.push(...elmsOutLevel)
      return newArray
    },
  },
}
</script>
