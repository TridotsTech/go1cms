<template>
  <LayoutHeader>
    <template #left-header>
      <Breadcrumbs :items="breadcrumbs" />
    </template>
    <template #right-header>
      <div class="flex gap-2 justify-end" v-if="alreadyActions">
        <Button
          variant="subtle"
          theme="gray"
          size="md"
          :label="__('Cancel')"
          :disabled="!dirty"
          @click="cancelSaveDoc"
        ></Button>
        <Button
          :variant="'solid'"
          theme="blue"
          size="md"
          :label="__('Save')"
          :disabled="!dirty"
          @click="callUpdateDoc"
        >
        </Button>
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
    <div v-if="JSON.stringify(_settings) != '{}'">
      <FieldsComponent
        :title="__('General Settings')"
        v-model="_settings.fields_cp"
      ></FieldsComponent>
      <div class="p-6 border border-gray-300 rounded-sm mb-4">
        <div class="mb-4 font-bold text-xl">{{ __('Instructions') }}</div>
        <div class="text-base py-4 border-t">
          <div class="font-bold text-lg mb-4">
            {{ __('Variables used in the email template') }}
          </div>
          <div class="mb-4">
            <SectionDropdown :label="__('Commonly used variables')">
              <template #content>
                <div class="text-gray-600">
                  <div class="mb-2">
                    <strong v-pre>{{ time }}: </strong>
                    <span>{{ __('creation time') }}</span>
                  </div>
                  <div class="mb-2">
                    <strong v-pre>{{ full_name }}: </strong>
                    <span>{{ __('customer full name') }}</span>
                  </div>
                  <div class="mb-2">
                    <strong v-pre>{{ phone_number }}: </strong>
                    <span>{{ __('customer phone number') }}</span>
                  </div>
                  <div class="mb-2">
                    <strong v-pre>{{ email }}: </strong>
                    <span>{{ __('customer email') }}</span>
                  </div>
                </div>
              </template>
            </SectionDropdown>
          </div>
          <div class="mb-4">
            <SectionDropdown
              :label="__('Variables used in the new contact template')"
            >
              <template #content>
                <div class="text-gray-600">
                  <div class="mb-2">
                    <strong v-pre>{{ address }}: </strong>
                    <span>{{ __('customer address') }}</span>
                  </div>
                  <div class="mb-2">
                    <strong v-pre>{{ content }}: </strong>
                    <span>{{ __('message content from customer') }}</span>
                  </div>
                  <div class="mb-2">
                    <strong v-pre>{{ source }}: </strong>
                    <span>{{ __('customer source') }}</span>
                  </div>
                  <div class="mb-2">
                    <strong v-pre>{{ utm_source }}: </strong>
                    <span>utm source</span>
                  </div>
                  <div class="mb-2">
                    <strong v-pre>{{ utm_campaign }}: </strong>
                    <span>utm campaign</span>
                  </div>
                  <div class="mb-2">
                    <strong v-pre>{{ sent_time }}: </strong>
                    <span>{{ __('submission time') }}</span>
                  </div>
                  <div class="mb-2">
                    <strong v-pre>{{ redirect_to }}: </strong>
                    <span>{{ __('link to view new contact details') }}</span>
                  </div>
                </div>
              </template>
            </SectionDropdown>
          </div>
          <div class="mb-4">
            <SectionDropdown
              :label="
                __('Variables used in the new account registration template')
              "
            >
              <template #content>
                <div class="text-gray-600">
                  <div class="mb-2">
                    <strong v-pre>{{ redirect_to }}: </strong>
                    <span>{{
                      __(
                        'link to view new account details (for admin) / login page link (for customer)',
                      )
                    }}</span>
                  </div>
                </div>
              </template>
            </SectionDropdown>
          </div>
          <div class="mb-4">
            <SectionDropdown
              :label="
                __('Variables used in the new job application CV template')
              "
            >
              <template #content>
                <div class="text-gray-600">
                  <div class="mb-2">
                    <strong v-pre>{{ job_title }}: </strong>
                    <span>{{ __('job title') }}</span>
                  </div>
                  <div class="mb-2">
                    <strong v-pre>{{ designation }}: </strong>
                    <span>{{ __('job position') }}</span>
                  </div>
                  <div class="mb-2">
                    <strong v-pre>{{ location }}: </strong>
                    <span>{{ __('work location') }}</span>
                  </div>
                  <div class="mb-2">
                    <strong v-pre>{{ employment_type }}: </strong>
                    <span>{{ __('employment type') }}</span>
                  </div>
                  <div class="mb-2">
                    <strong v-pre>{{ department }}: </strong>
                    <span>{{ __('department') }}</span>
                  </div>
                  <div class="mb-2">
                    <strong v-pre>{{ lower_range }}: </strong>
                    <span>{{ __('minimum salary') }}</span>
                  </div>
                  <div class="mb-2">
                    <strong v-pre>{{ upper_range }}: </strong>
                    <span>{{ __('maximum salary') }}</span>
                  </div>
                  <div class="mb-2">
                    <strong v-pre>{{ currency }}: </strong>
                    <span>{{ __('currency') }}</span>
                  </div>
                  <div class="mb-2">
                    <strong v-pre>{{ salary_per }}: </strong>
                    <span>{{ __('salary paid by month/year') }}</span>
                  </div>
                  <div class="mb-2">
                    <strong v-pre>{{ content }}: </strong>
                    <span>{{ __('customer-submitted content') }}</span>
                  </div>
                  <div class="mb-2">
                    <strong v-pre>{{ redirect_to }}: </strong>
                    <span>{{ __('application detail link') }}</span>
                  </div>
                </div>
              </template>
            </SectionDropdown>
          </div>
          <div class="mb-4">
            <SectionDropdown
              :label="__('Variables used in the order template')"
            >
              <template #content>
                <div class="text-gray-600">
                  <div class="mb-2">
                    <strong v-pre>{{ order_code }}: </strong>
                    <span>{{ __('order code') }}</span>
                  </div>
                  <div class="mb-2">
                    <strong v-pre>{{ order_status }}: </strong>
                    <span>{{ __('order status') }}</span>
                  </div>
                  <div class="mb-2">
                    <strong v-pre>{{ address }}: </strong>
                    <span>{{ __('customer address') }}</span>
                  </div>
                  <div class="mb-2">
                    <div>
                      <strong v-pre>items: </strong>
                      <span>{{ __('product list') }}</span>
                    </div>
                    <div class="flex flex-col gap-2 m-2">
                      <div>
                        -
                        <strong v-pre>item: </strong>
                        <span>{{
                          __('variable containing information of one product')
                        }}</span>
                      </div>
                      <div>
                        -
                        <strong v-pre>{% for item in items %}: </strong>
                        <span>{{ __('loop start variable') }}</span>
                      </div>
                      <div>
                        -
                        <strong v-pre>{{ item.item_name }}: </strong>
                        <span>{{ __('product name') }}</span>
                      </div>
                      <div>
                        -
                        <strong v-pre>{{ item.rate }}: </strong>
                        <span>{{ __('unit price per product') }}</span>
                      </div>
                      <div>
                        -
                        <strong v-pre>{{ item.qty }}: </strong>
                        <span>{{ __('product quantity') }}</span>
                      </div>
                      <div>
                        -
                        <strong v-pre>{{ item.amount }}: </strong>
                        <span>{{ __('total amount for one product') }}</span>
                      </div>
                      <div>
                        -
                        <strong v-pre>{% endfor %}: </strong>
                        <span>{{ __('loop end variable') }}</span>
                      </div>
                    </div>
                  </div>
                  <div class="mb-2">
                    <strong v-pre>{{ grand_total }}: </strong>
                    <span>{{ __('subtotal amount') }}</span>
                  </div>
                  <div class="mb-2">
                    <strong v-pre>{{ redirect_to }}: </strong>
                    <span>
                      {{
                        __(
                          'order detail link (for admin) / order view link (for customer)',
                        )
                      }}
                    </span>
                  </div>
                </div>
              </template>
            </SectionDropdown>
          </div>
        </div>
      </div>
    </div>
    <div v-else class="p-4 border border-gray-300 rounded-sm mb-4">
      <div class="flex justify-center h-screen mt-40 text-gray-700">
        <LoadingIndicator class="h-8 w-8" />
      </div>
    </div>
  </div>
</template>

<script setup>
import LayoutHeader from '@/components/LayoutHeader.vue'
import SectionDropdown from '@/components/SectionDropdown.vue'
import FieldsComponent from '@/components/FieldsPage/FieldsComponent.vue'
import { Breadcrumbs, ErrorMessage, createResource, call } from 'frappe-ui'
import { ref, computed, watch } from 'vue'
import { createToast, errorMessage, validErrApi } from '@/utils'
import { globalStore } from '@/stores/global'
import { useRouter } from 'vue-router'
const router = useRouter()
import { viewsStore } from '@/stores/views'

const { views } = viewsStore()
const { changeLoadingValue } = globalStore()

const breadcrumbs = [{ label: __('Settings'), route: { name: 'CMS Settings' } }]
const _settings = ref({})
const msgError = ref()

// get detail
const settings = createResource({
  url: 'go1_cms.api.settings.get_setup',
  method: 'GET',
  auto: true,
  transform: (data) => {
    _settings.value = JSON.parse(JSON.stringify(data))
    return data
  },
  onError: (err) => {
    validErrApi(err, router)
    if (err.messages && err.messages.length) {
      msgError.value = err.messages.join(', ')
      errorMessage(__('An error has occurred'), err.messages.join(', '))
    } else {
      errorMessage(__('An error has occurred'), err)
    }
  },
})

// handle allow actions
const alreadyActions = ref(false)
const dirty = computed(() => {
  if (_settings.value?.fields_cp) {
    let show_edit = false
    if (_settings.value?.fields_cp[0].fields[0].content) {
      show_edit = true
    }
    _settings.value.fields_cp[0].fields[1].show_edit = show_edit

    show_edit = false
    if (_settings.value?.fields_cp[1].fields[1].content) {
      show_edit = true
    }
    _settings.value.fields_cp[1].fields[2].show_edit = show_edit
  }
  return JSON.stringify(settings.data) !== JSON.stringify(_settings.value)
})

watch(dirty, (val) => {
  alreadyActions.value = true
})

async function callUpdateDoc() {
  changeLoadingValue(true, __('Saving...'))
  try {
    let data = JSON.parse(JSON.stringify(_settings.value))

    let docUpdate = await call('go1_cms.api.settings.update_setup', {
      data: data,
    })

    if (docUpdate.name) {
      settings.reload()
      views.reload()

      createToast({
        title: __('Saved'),
        icon: 'check',
        iconClasses: 'text-green-600',
      })
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

async function cancelSaveDoc() {
  await settings.reload()
}
</script>
