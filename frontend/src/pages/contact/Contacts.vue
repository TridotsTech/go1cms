<template>
  <LayoutHeader>
    <template #left-header>
      <Breadcrumbs :items="breadcrumbs" />
    </template>
    <template #right-header></template>
  </LayoutHeader>
  <div class="flex-1 flex flex-col h-full overflow-auto p-6 pt-2 pb-4">
    <ViewControls
      ref="viewControls"
      v-model="contacts"
      v-model:loadMore="loadMore"
      v-model:resizeColumn="triggerResize"
      v-model:updatedPageCount="updatedPageCount"
      :options="{
        hideColumnsButton: false,
      }"
      doctype="MBW Contact"
    />
    <ContactListView
      v-if="contacts.data && rows.length"
      v-model="contacts.data.page_length_count"
      v-model:list="contacts"
      :rows="rows"
      :columns="columns"
      :options="{
        rowCount: contacts.data.row_count,
        totalCount: contacts.data.total_count,
        selectable: false,
        showTooltip: false,
        resizeColumn: true,
      }"
      @loadMore="() => loadMore++"
      @columnWidthUpdated="() => triggerResize++"
      @updatePageCount="(count) => (updatedPageCount = count)"
      @applyFilter="(data) => viewControls.applyFilter(data)"
    ></ContactListView>
    <div
      v-else-if="contacts.data"
      class="flex flex-1 items-center justify-center"
    >
      <div
        class="flex flex-col items-center gap-3 text-xl font-medium text-gray-500"
      >
        <ContactsIconV1 class="h-10 w-10" />
        <span>{{ __('No contacts available') }}</span>
      </div>
    </div>
  </div>
</template>

<script setup>
import LayoutHeader from '@/components/LayoutHeader.vue'
import ContactsIconV1 from '@/components/Icons/ContactsIconV1.vue'
import ContactListView from '@/components/ListViews/ContactListView.vue'
import ViewControls from '@/components/ViewControls.vue'
import { Breadcrumbs } from 'frappe-ui'
import { ref, computed } from 'vue'

const breadcrumbs = [{ label: __('Contact List'), route: { name: 'Contacts' } }]

// leads data is loaded in the ViewControls component
const contacts = ref({})
const loadMore = ref(1)
const triggerResize = ref(1)
const updatedPageCount = ref(20)
const viewControls = ref(null)

// Columns
const columns = computed(() => {
  if (!contacts.value?.data?.columns) return []

  let _columns = contacts.value?.data?.columns
  if (!_columns.find((el) => el.key == 'action_button')) {
    _columns.push({ label: __('Action'), key: 'action_button' })
  }
  return _columns
})

// Rows
const rows = computed(() => {
  if (!contacts.value?.data?.data) return []
  return contacts.value?.data.data.map((cat) => {
    let _rows = {}
    contacts.value?.data.rows.forEach((row) => {
      _rows[row] = cat[row]
    })
    _rows['action_button'] = { ...cat }
    return _rows
  })
})
</script>
