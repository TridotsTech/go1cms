<template>
  <div v-if="field.label" class="mb-2 text-sm text-gray-600">
    {{ __(field.label) }}
    <span class="text-red-500" v-if="field.mandatory">*</span>
  </div>
  <FormControl
    v-if="field.type === 'select'"
    type="select"
    class="form-control"
    :disabled="field.disabled"
    :class="field.prefix ? 'prefix' : ''"
    :options="field.options"
    v-model="data"
    :placeholder="__(field.placeholder)"
  >
    <template v-if="field.prefix" #prefix>
      <IndicatorIcon :class="field.prefix" />
    </template>
  </FormControl>
  <div v-else-if="field.type === 'link'">
    <Link
      class="form-control"
      :value="data"
      :doctype="field.doctype"
      @change="
        (v) => {
          data = v
          if (Array.isArray(actions) && actions.length) {
            actions[2] = v
          }
        }
      "
      :placeholder="__(field.placeholder)"
      :onCreate="field.create"
      :filters="field.filters"
    />
    <div v-if="Array.isArray(actions) && actions.length">
      <div class="flex flex-wrap gap-2 text-sm my-1 text-gray-600">
        <div v-if="actions[1]">
          <a
            class="text-blue-500 underline"
            :href="actions[0] + actions[1]"
            target="_blank"
            rel=""
            >{{ __('Add New') }}</a
          >
        </div>
        <div v-if="actions[2]">
          {{ __('or') }}
          <a
            class="text-blue-500 underline"
            :href="actions[0] + actions[2]"
            target="_blank"
            rel=""
            >{{ __('Edit') }}</a
          >
        </div>
      </div>
    </div>
    <div
      v-if="field.description"
      v-html="field.description"
      class="text-sm my-1 text-gray-600"
    ></div>
  </div>
  <MultiselectLink
    v-else-if="field.type === 'multilink'"
    class="form-control"
    v-model="data"
    :doctype="field.doctype"
    :placeholder="__(field.placeholder)"
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
    :placeholder="__(field.placeholder)"
    v-model="data"
  />
  <UploadFileImage
    v-else-if="field.type === 'upload_image'"
    title=""
    v-model:refImg="refImgMeta"
    v-model="data"
  >
    <template #preview>
      <div
        class="border p-2 flex justify-center"
        :class="field.classSize ? field.classSize : 'h-48 max-w-48'"
      >
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
  <div v-else-if="['Small Text', 'textarea'].includes(field.type)">
    <FormControl
      type="textarea"
      :placeholder="__(field.placeholder)"
      v-model="data"
      :rows="field.rows"
    />
    <p v-if="field.description" class="text-sm my-1 text-gray-600">
      <strong>Chú thích: </strong>{{ field.description }}
    </p>
  </div>
  <Ckeditor
    v-else-if="['texteditor', 'Text Editor'].includes(field.type)"
    v-model="data"
  ></Ckeditor>
  <Ckeditor
    v-else-if="['Long Text'].includes(field.type)"
    modeConfig="textarea"
    v-model="data"
  ></Ckeditor>
  <!-- <TextEditor
    v-else-if="field.type === 'texteditor'"
    variant="outline"
    editor-class="!prose-sm overflow-auto min-h-[180px] max-h-80 py-1.5 px-2 border border-gray-300 bg-white hover:border-gray-400 hover:shadow-sm focus:bg-white focus:border-gray-500 focus:shadow-sm focus:ring-0 focus-visible:ring-2 focus-visible:ring-gray-400 text-gray-800 transition-colors min-w-full"
    :fixedMenu="true"
    :content="data"
    @change="(val) => (data = val)"
  ></TextEditor> -->
  <!-- <CustomQuillEditor
    v-else-if="field.type === 'texteditor'"
    classHeightscreen="max-h-80"
    classQuill="overflow-auto min-h-80"
    v-model="data"
  ></CustomQuillEditor> -->
  <div v-else-if="field.type === 'checkbox'">
    <div class="flex">
      <FormControl
        :disabled="field.disabled"
        :id="field.name"
        type="checkbox"
        v-model="data"
      />
      <label
        v-if="field.labelInput"
        class="ml-2 text-sm text-gray-600"
        :for="field.name"
      >
        {{ __(field.labelInput) }}
      </label>
    </div>
    <div
      v-if="field.description"
      v-html="field.description"
      class="text-sm my-1 text-gray-600"
    ></div>
  </div>
  <FormControl
    v-else-if="['number', 'Int'].includes(field.type)"
    type="number"
    :placeholder="__(field.placeholder)"
    v-model="data"
    :disabled="field.disabled || false"
  />
  <div v-else>
    <FormControl
      type="text"
      :placeholder="__(field.placeholder)"
      v-model="data"
      :disabled="field.disabled"
    />
    <div v-if="field.description" class="text-sm my-1 text-gray-600">
      <span v-html="field.label_des"></span>
      <span>{{ field.description }}</span>
    </div>
  </div>
</template>

<script setup>
import Ckeditor from '@/components/Ckeditor.vue'
import UploadFileImage from '@/components/UploadFileImage.vue'
import NestedPopover from '@/components/NestedPopover.vue'
import DropdownItem from '@/components/DropdownItem.vue'
import IndicatorIcon from '@/components/Icons/IndicatorIcon.vue'
import ImageEmptyIcon from '@/components/Icons/ImageEmptyIcon.vue'
import UserAvatar from '@/components/UserAvatar.vue'
import Link from '@/components/Controls/Link.vue'
import MultiselectLink from '@/components/Controls/MultiselectLink.vue'
import { usersStore } from '@/stores/users'
import { Tooltip, TextEditor, DatePicker } from 'frappe-ui'
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
const actions = defineModel('actions')
const refImgMeta = ref(null)

watch(
  () => props.imgPreview,
  (val, oldVal) => {
    updateUrlImage()
  },
)

watch(
  () => data.value,
  (val, oldVal) => {
    updateUrlImage()
  },
)

onMounted(() => {
  updateUrlImage()
})

function updateUrlImage() {
  if (!data.value && refImgMeta.value && props.imgPreview) {
    refImgMeta.value.src = props.imgPreview
  }
}
</script>

<style scoped>
:deep(.form-control.prefix select) {
  padding-left: 2rem;
}
</style>
