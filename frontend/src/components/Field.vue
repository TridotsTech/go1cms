<template>
  <div v-if="field.label" class="mb-2 text-sm text-gray-600">
    {{ __(field.label) }}
    <span class="text-red-500" v-if="field.mandatory">*</span>
  </div>
  <FormControl
    v-if="field.type === 'select'"
    type="select"
    class="form-control"
    :class="field.prefix ? 'prefix' : ''"
    :options="field.options"
    v-model="data"
    :placeholder="__(field.placeholder)"
  >
    <template v-if="field.prefix" #prefix>
      <IndicatorIcon :class="field.prefix" />
    </template>
  </FormControl>
  <Link
    v-else-if="field.type === 'link'"
    class="form-control"
    :value="data"
    :doctype="field.doctype"
    @change="(v) => (data = v)"
    :placeholder="__(field.placeholder)"
    :onCreate="field.create"
  />
  <Link
    v-else-if="field.type === 'user'"
    class="form-control"
    :value="getUser(data).full_name"
    :doctype="field.doctype"
    @change="(v) => (data = v)"
    :placeholder="__(field.placeholder)"
    :hideMe="true"
  >
    <template #prefix>
      <UserAvatar class="mr-2" :user="data" size="sm" />
    </template>
    <template #item-prefix="{ option }">
      <UserAvatar class="mr-2" :user="option.value" size="sm" />
    </template>
    <template #item-label="{ option }">
      <Tooltip :text="option.value">
        <div class="cursor-pointer">
          {{ getUser(option.value).full_name }}
        </div>
      </Tooltip>
    </template>
  </Link>
  <div v-else-if="field.type === 'dropdown'">
    <NestedPopover>
      <template #target="{ open }">
        <Button
          :label="data"
          class="dropdown-button flex w-full items-center justify-between rounded border border-gray-100 bg-gray-100 px-2 py-1.5 text-base text-gray-800 placeholder-gray-500 transition-colors hover:border-gray-200 hover:bg-gray-200 focus:border-gray-500 focus:bg-white focus:shadow-sm focus:outline-none focus:ring-0 focus-visible:ring-2 focus-visible:ring-gray-400"
        >
          <div class="truncate">{{ data }}</div>
          <template #suffix>
            <FeatherIcon
              :name="open ? 'chevron-up' : 'chevron-down'"
              class="h-4 text-gray-600"
            />
          </template>
        </Button>
      </template>
      <template #body>
        <div
          class="my-2 space-y-1.5 divide-y rounded-lg border border-gray-100 bg-white p-1.5 shadow-xl"
        >
          <div>
            <DropdownItem
              v-if="field.options?.length"
              v-for="option in field.options"
              :key="option.name"
              :option="option"
            />
            <div v-else>
              <div class="p-1.5 px-7 text-base text-gray-500">
                {{ __('No {0} Available', [field.label]) }}
              </div>
            </div>
          </div>
          <div class="pt-1.5">
            <Button
              variant="ghost"
              class="w-full !justify-start"
              :label="__('Create New')"
              @click="field.create()"
            >
              <template #prefix>
                <FeatherIcon name="plus" class="h-4" />
              </template>
            </Button>
          </div>
        </div>
      </template>
    </NestedPopover>
  </div>
  <DatePicker
    v-else-if="field.type === 'date'"
    type="date"
    icon-left="calendar"
    :placeholder="__(field.placeholder)"
    :value="data"
    @change="
      (v) => {
        data = v
      }
    "
  />
  <UploadFileImage
    v-else-if="field.type === 'upload_image'"
    title=""
    v-model:refImg="refImgMeta"
    v-model="data"
  >
    <template #preview>
      <div class="border max-h-48 p-2 flex justify-center">
        <ImageEmptyIcon
          :class="data || imgPreview ? 'hidden' : ''"
          class="text-gray-400 h-full w-full"
        ></ImageEmptyIcon>
        <img
          :class="!data && !imgPreview ? 'hidden' : ''"
          ref="refImgMeta"
          class="h-full w-full"
          :src="refImgMeta?.src"
          alt=""
        />
      </div>
    </template>
  </UploadFileImage>
  <FormControl
    v-else-if="field.type === 'textarea'"
    type="textarea"
    :placeholder="__(field.placeholder)"
    v-model="data"
    :rows="field.rows"
  />
  <TextEditor
    v-else-if="field.type === 'texeditor'"
    variant="outline"
    editor-class="!prose-sm overflow-auto min-h-[180px] max-h-80 py-1.5 px-2 border border-gray-300 bg-white hover:border-gray-400 hover:shadow-sm focus:bg-white focus:border-gray-500 focus:shadow-sm focus:ring-0 focus-visible:ring-2 focus-visible:ring-gray-400 text-gray-800 transition-colors min-w-full"
    fixedMenu="true"
    :content="data"
    @change="(val) => (data = val)"
  ></TextEditor>
  <!-- <CustomQuillEditor
    v-else-if="field.type === 'texeditor'"
    classHeightscreen="max-h-80"
    classQuill="overflow-auto min-h-80"
    v-model="data"
  ></CustomQuillEditor> -->
  <div class="flex" v-else-if="field.type === 'checkbox'">
    <FormControl :id="field.name" type="checkbox" v-model="data" />
    <label
      v-if="field.labelInput"
      class="ml-2 text-sm text-gray-600"
      :for="field.name"
      >{{ field.labelInput }}</label
    >
  </div>
  <FormControl
    v-else
    type="text"
    :placeholder="__(field.placeholder)"
    v-model="data"
  />
</template>

<script setup>
import DatePicker from '@/components/Controls/DatePicker.vue'
import UploadFileImage from '@/components/UploadFileImage.vue'
import NestedPopover from '@/components/NestedPopover.vue'
import DropdownItem from '@/components/DropdownItem.vue'
import IndicatorIcon from '@/components/Icons/IndicatorIcon.vue'
import ImageEmptyIcon from '@/components/Icons/ImageEmptyIcon.vue'
import UserAvatar from '@/components/UserAvatar.vue'
import Link from '@/components/Controls/Link.vue'
import { usersStore } from '@/stores/users'
import { Tooltip, TextEditor } from 'frappe-ui'
import { ref, watch, onMounted } from 'vue'

const { getUser } = usersStore()

const props = defineProps({
  field: Object,
  imgPreview: {
    type: String,
    default: null,
  },
})
const data = defineModel()
const refImgMeta = ref(null)

watch(
  () => props.imgPreview,
  (val, oldVal) => {
    if (!data.value && refImgMeta.value) {
      refImgMeta.value.src = props.imgPreview
    }
  }
)

onMounted(() => {
  if (!data.value && refImgMeta.value) {
    refImgMeta.value.src = props.imgPreview
  }
})
</script>

<style scoped>
:deep(.form-control.prefix select) {
  padding-left: 2rem;
}
</style>
