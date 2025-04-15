<template>
  <LayoutHeader>
    <template #left-header>
      <Breadcrumbs :items="breadcrumbs" />
    </template>
    <template #right-header>
      <div class="flex gap-2 justify-end" v-if="alreadyActions">
        <Dropdown
          :options="[
            {
              group: __('Delete'),
              items: [
                {
                  label: __('Delete contact'),
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
          :label="__('Cancel')"
          @click="contact.reload()"
          :disabled="!dirty"
        ></Button>
        <Button
          variant="solid"
          theme="blue"
          size="md"
          :label="__('Save')"
          @click="callUpdateDoc"
          :disabled="!dirty"
        ></Button>
      </div>
    </template>
  </LayoutHeader>
  <div class="p-6 overflow-auto">
    <div v-if="msgError" class="p-4 border border-gray-300 rounded-sm mb-4">
      <div class="text-base text-red-600 font-bold mb-2">
        {{ __('An error has occurred') }}:
      </div>
      <ErrorMessage :message="msgError" />
    </div>
    <div v-if="_contact" class="p-4 border border-gray-300 rounded-sm mb-4">
      <div class="mb-5">
        <Fields :sections="sections" :data="_contact" />
      </div>
    </div>
    <div v-else class="p-4 border border-gray-300 rounded-sm mb-4">
      <div class="flex justify-center h-screen mt-40 text-gray-700">
        <LoadingIndicator class="h-8 w-8" />
      </div>
    </div>
  </div>
  <Dialog
    :options="{
      title: __('Delete contact'),
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
          {{ __('Are you sure you want to delete the contact') }}:
          <b>"{{ _contact?.email }}"</b>?
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
import { createToast, errorMessage, warningMessage, validErrApi } from '@/utils'
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
          label: 'Last name',
          mandatory: false,
          name: 'last_name',
          type: 'data',
          placeholder: 'Last name',
        },
        {
          label: 'First name',
          mandatory: false,
          name: 'first_name',
          type: 'data',
          placeholder: 'First name',
        },
        {
          label: 'Full name',
          mandatory: false,
          name: 'full_name',
          type: 'data',
          placeholder: 'Full name',
        },
        {
          label: 'Email',
          mandatory: false,
          name: 'email',
          type: 'data',
          placeholder: 'Email',
        },
        {
          label: 'Phone number',
          mandatory: false,
          name: 'phone_number',
          type: 'data',
          placeholder: 'Phone',
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
          label: 'Message',
          name: 'message',
          type: 'textarea',
          placeholder: 'Message',
          rows: 10,
        },
        {
          label: 'Source',
          name: 'source',
          type: 'textarea',
          placeholder: 'Source',
          rows: 10,
        },
        {
          label: 'UTM Source',
          mandatory: false,
          name: 'utm_source',
          type: 'data',
          placeholder: 'Utm source',
        },
        {
          label: 'Utm Campaign',
          mandatory: false,
          name: 'utm_campaign',
          type: 'data',
          placeholder: 'Utm campaign',
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
  onError: (err) => {
    validErrApi(err, router)
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
    warningMessage(__('No changes in document'))
    return
  }

  changeLoadingValue(true, __('Saving...'))
  try {
    const doc = await call('go1_cms.api.mbw_contact.update_contact', {
      data: {
        ..._contact.value,
      },
    })
    if (doc.name) {
      createToast({
        title: __('Saved'),
        icon: 'check',
        iconClasses: 'text-green-600',
      })
      contact.reload()
    }
  } catch (err) {
    validErrApi(err, router)
    if (err.messages && err.messages.length) {
      msgError.value = err.messages.join(', ')
      errorMessage(__('An error has occurred'), err.messages.join(', '))
    } else {
      errorMessage(__('An error has occurred'), err)
    }
  }
  changeLoadingValue(false)
}

async function deleteDoc(close) {
  changeLoadingValue(true, __('Deleting...'))
  try {
    await call('go1_cms.api.mbw_contact.delete_contact', {
      name: props.contactId,
    }).then(() => {
      createToast({
        title: __('Deleted'),
        icon: 'check',
        iconClasses: 'text-green-600',
      })
      close()
      router.push({
        name: 'Contacts',
      })
    })
  } catch (err) {
    validErrApi(err, router)
    if (err.messages && err.messages.length) {
      msgError.value = err.messages.join(', ')
      errorMessage(__('An error has occurred'), err.messages.join(', '))
    } else {
      errorMessage(__('An error has occurred'), err)
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
  let items = [{ label: __('Contact List'), route: { name: 'Contacts' } }]
  items.push({
    label:
      contact.data?.email ||
      contact.data?.full_name ||
      contact.data?.phone_number,
    route: {},
  })
  return items
})
</script>
