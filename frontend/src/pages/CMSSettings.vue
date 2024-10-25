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
          label="Hủy"
          :disabled="!dirty"
          @click="cancelSaveDoc"
        ></Button>
        <Button
          :variant="'solid'"
          theme="blue"
          size="md"
          label="Lưu"
          :disabled="!dirty"
          @click="callUpdateDoc"
        >
        </Button>
      </div>
    </template>
  </LayoutHeader>
  <div class="p-6 overflow-auto">
    <div v-if="msgError" class="p-4 border border-gray-300 rounded-sm mb-4">
      <div class="text-base text-red-600 font-bold mb-2">Có lỗi xảy ra:</div>
      <ErrorMessage :message="msgError" />
    </div>
    <div v-if="JSON.stringify(_settings) != '{}'">
      <FieldsComponent
        title="Cài đặt chung"
        v-model="_settings.fields_cp"
      ></FieldsComponent>
      <div class="p-6 border border-gray-300 rounded-sm mb-4">
        <div class="mb-4 font-bold text-xl">Hướng dẫn</div>
        <div class="text-base py-4 border-t">
          <div class="font-bold text-lg mb-4">
            Các biến được dùng trong mẫu email
          </div>
          <div class="mb-4">
            <SectionDropdown label="Các biến sử dụng chung">
              <template #content>
                <div class="text-gray-600">
                  <div class="mb-2">
                    <strong v-pre>{{ time }}: </strong>
                    <span>thời gian tạo</span>
                  </div>
                  <div class="mb-2">
                    <strong v-pre>{{ full_name }}: </strong>
                    <span>họ và tên khách hàng</span>
                  </div>
                  <div class="mb-2">
                    <strong v-pre>{{ phone_number }}: </strong>
                    <span>số điện thoại khách hàng</span>
                  </div>
                  <div class="mb-2">
                    <strong v-pre>{{ email }}: </strong>
                    <span>email khách hàng</span>
                  </div>
                </div>
              </template>
            </SectionDropdown>
          </div>
          <div class="mb-4">
            <SectionDropdown label="Các biến sử dụng trong mẫu có liên hệ mới">
              <template #content>
                <div class="text-gray-600">
                  <div class="mb-2">
                    <strong v-pre>Bao gồm các biến sử dụng chung.</strong>
                  </div>
                  <div class="mb-2">
                    <strong v-pre>{{ address }}: </strong>
                    <span>địa chỉ khách hàng</span>
                  </div>
                  <div class="mb-2">
                    <strong v-pre>{{ content }}: </strong>
                    <span>nội dung khách hàng gửi kèm</span>
                  </div>
                  <div class="mb-2">
                    <strong v-pre>{{ source }}: </strong>
                    <span>nguồn gửi của khách hàng</span>
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
                    <strong v-pre>{{ send_time }}: </strong>
                    <span>thời gian gửi</span>
                  </div>
                  <div class="mb-2">
                    <strong v-pre>{{ redirect_to }}: </strong>
                    <span>đường dẫn tới xem chi tiết cho quản trị viên</span>
                  </div>
                </div>
              </template>
            </SectionDropdown>
          </div>
          <div class="mb-4">
            <SectionDropdown
              label="Các biến sử dụng trong mẫu tài khoản đăng ký mới"
            >
              <template #content>
                <div class="text-gray-600">
                  <div class="mb-2">
                    <strong v-pre>Bao gồm các biến sử dụng chung.</strong>
                  </div>
                </div>
              </template>
            </SectionDropdown>
          </div>
          <div class="mb-4">
            <SectionDropdown
              label="Các biến sử dụng trong mẫu có CV ứng tuyển mới"
            >
              <template #content>
                <div class="text-gray-600">
                  <div class="mb-2">
                    <strong v-pre>Bao gồm các biến sử dụng chung.</strong>
                  </div>
                  <div class="mb-2">
                    <strong v-pre>{{ job_title }}: </strong>
                    <span>tên công việc</span>
                  </div>
                  <div class="mb-2">
                    <strong v-pre>{{ designation }}: </strong>
                    <span>vị trí công việc</span>
                  </div>
                  <div class="mb-2">
                    <strong v-pre>{{ location }}: </strong>
                    <span>nơi làm việc</span>
                  </div>
                  <div class="mb-2">
                    <strong v-pre>{{ employment_type }}: </strong>
                    <span>hình thức làm việc</span>
                  </div>
                  <div class="mb-2">
                    <strong v-pre>{{ department }}: </strong>
                    <span>phòng ban</span>
                  </div>
                  <div class="mb-2">
                    <strong v-pre>{{ lower_range }}: </strong>
                    <span>lương tối thiểu</span>
                  </div>
                  <div class="mb-2">
                    <strong v-pre>{{ upper_range }}: </strong>
                    <span>lương giới hạn</span>
                  </div>
                  <div class="mb-2">
                    <strong v-pre>{{ currency }}: </strong>
                    <span>đơn vị tiền tệ</span>
                  </div>
                  <div class="mb-2">
                    <strong v-pre>{{ salary_per }}: </strong>
                    <span>lương trả theo tháng/năm</span>
                  </div>
                  <div class="mb-2">
                    <strong v-pre>{{ content }}: </strong>
                    <span>nội dung khách hàng gửi kèm</span>
                  </div>
                  <div class="mb-2">
                    <strong v-pre>{{ redirect_to }}: </strong>
                    <span>đường dẫn tới xem chi tiết cho quản trị viên</span>
                  </div>
                </div>
              </template>
            </SectionDropdown>
          </div>
          <div class="mb-4">
            <SectionDropdown label="Các biến sử dụng trong mẫu đơn hàng">
              <template #content>
                <div class="text-gray-600">
                  <div class="mb-2">
                    <strong v-pre>Bao gồm các biến sử dụng chung.</strong>
                  </div>
                  <div class="mb-2">
                    <strong v-pre>{{ order_code }}: </strong>
                    <span>mã đơn hàng</span>
                  </div>
                  <div class="mb-2">
                    <strong v-pre>{{ order_status }}: </strong>
                    <span>trạng thái đơn hàng</span>
                  </div>
                  <div class="mb-2">
                    <strong v-pre>{{ address }}: </strong>
                    <span>địa chỉ khách hàng</span>
                  </div>
                  <div class="mb-2">
                    <strong v-pre>{{ redirect_to }}: </strong>
                    <span
                      >đường dẫn tới xem chi tiết cho quản trị viên / cho khách
                      hàng</span
                    >
                  </div>
                  <div class="mb-2">
                    <div>
                      <strong v-pre>items: </strong>
                      <span>danh sách sản phẩm</span>
                    </div>
                    <div class="flex flex-col gap-2 m-2">
                      <div>
                        -
                        <strong v-pre>item: </strong>
                        <span>biến chứa thông tin của 1 sản phẩm</span>
                      </div>
                      <div>
                        -
                        <strong v-pre>{% for item in items %}: </strong>
                        <span>biến mở vòng lặp</span>
                      </div>
                      <div>
                        -
                        <strong v-pre>{{ item.item_name }}: </strong>
                        <span>tên của sản phẩm</span>
                      </div>
                      <div>
                        -
                        <strong v-pre>{{ item.rate }}: </strong>
                        <span>đơn giá / 1 đơn vị sản phẩm</span>
                      </div>
                      <div>
                        -
                        <strong v-pre>{{ item.qty }}: </strong>
                        <span>số lượng của 1 sản phẩm</span>
                      </div>
                      <div>
                        -
                        <strong v-pre>{{ item.amount }}: </strong>
                        <span>tổng số tiền của 1 sản phẩm</span>
                      </div>
                      <div>
                        -
                        <strong v-pre>{% endfor %}: </strong>
                        <span>biến đóng vòng lặp</span>
                      </div>
                    </div>
                  </div>
                  <div class="mb-2">
                    <strong v-pre>{{ grand_total }}: </strong>
                    <span>tổng số tiền tạm tính</span>
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

const breadcrumbs = [{ label: 'Cài đặt', route: { name: 'CMS Settings' } }]
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
      errorMessage('Có lỗi xảy ra', err.messages.join(', '))
    } else {
      errorMessage('Có lỗi xảy ra', err)
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
  changeLoadingValue(true, 'Đang lưu...')
  try {
    let data = JSON.parse(JSON.stringify(_settings.value))

    let docUpdate = await call('go1_cms.api.settings.update_setup', {
      data: data,
    })

    if (docUpdate.name) {
      settings.reload()
      views.reload()

      createToast({
        title: 'Cập nhật thành công',
        icon: 'check',
        iconClasses: 'text-green-600',
      })
    }
  } catch (err) {
    validErrApi(err, router)
    if (err.messages && err.messages.length) {
      msgError.value = err.messages.join(', ')
      errorMessage('Có lỗi xảy ra', err.messages.join(', '))
    } else {
      errorMessage('Có lỗi xảy ra', err)
    }
  }
  changeLoadingValue(false)
}

async function cancelSaveDoc() {
  await settings.reload()
}
</script>
