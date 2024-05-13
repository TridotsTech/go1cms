<template>
  <LayoutHeader>
    <template #left-header>
      <Breadcrumbs :items="breadcrumbs" />
    </template>
  </LayoutHeader>
  <div class="p-6 mt-12">
    <div class="border-b mb-4 pb-2 border-gray-300">
      <div class="flex flex-wrap justify-between items-center gap-2">
        <h2 class="font-bold text-3xl">Thêm mới bài viết</h2>
        <div class="flex rounded-sm gap-2 justify-end">
          <Button
            :variant="'subtle'"
            theme="gray"
            size="md"
            label="Hủy"
            route="/posts"
          ></Button>
          <Button
            :variant="'solid'"
            theme="blue"
            size="md"
            label="Lưu"
          ></Button>
        </div>
      </div>
    </div>
    <div class="p-4 border border-gray-300 rounded-sm mb-4">
      <div class="p-2">
        <div>
          <div class="mb-4">
            <h2 class="font-bold text-xl">Thông tin cơ bản</h2>
          </div>
          <div class="grid lg:grid-cols-2 gap-4">
            <div class="flex flex-col gap-4">
              <FormControl
                :type="'text'"
                size="md"
                variant="subtle"
                placeholder="Nhập tiêu đề"
                label="Tiêu đề"
                v-model="inputValue"
              />
              <FormControl
                :type="'textarea'"
                size="md"
                variant="subtle"
                placeholder="Nhập giới thiệu"
                label="Giới thiệu bài viết"
                v-model="inputValue"
                rows="10"
              />
              <FormControl
                type="autocomplete"
                :options="[
                  {
                    label: 'One',
                    value: '1',
                  },
                  {
                    label: 'Two',
                    value: '2',
                  },
                  {
                    label: 'Three',
                    value: '3',
                  },
                ]"
                size="sm"
                variant="subtle"
                placeholder="Chọn danh mục"
                label="Danh mục"
                v-model="autocompleteValue"
              />
            </div>
            <div class="flex flex-col gap-4">
              <FormControl
                :type="'date'"
                size="md"
                variant="subtle"
                placeholder="dd/mm/yyyy"
                label="Ngày đăng"
                v-model="inputValue"
              />
              <UploadFileImage
                title="Ảnh bài viết"
                v-model:refImg="refImg"
                v-model:inputFile="inputFile"
              >
                <template #preview>
                  <div class="border p-2 flex justify-center">
                    <ImageEmptyIcon
                      :class="inputFile ? 'hidden' : ''"
                      class="text-gray-400 h-48"
                    ></ImageEmptyIcon>
                    <img
                      :class="!inputFile ? 'hidden' : ''"
                      ref="refImg"
                      class="h-48 w-full"
                      src=""
                      alt=""
                    />
                  </div>
                </template>
              </UploadFileImage>
            </div>
          </div>
        </div>
        <div class="mt-2 p-2 border-t">
          <div class="mt-2 mb-4">
            <h2 class="font-bold text-xl">SEO</h2>
          </div>
          <div class="my-2 grid lg:grid-cols-2 gap-4">
            <div class="flex flex-col gap-4">
              <FormControl
                :type="'text'"
                size="md"
                variant="subtle"
                placeholder="Nhập tiêu đề"
                label="Tiêu đề"
                v-model="inputValue"
              />
              <FormControl
                :type="'textarea'"
                size="md"
                variant="subtle"
                placeholder="Nhập mô tả"
                label="Thẻ mô tả"
                v-model="inputValue"
                rows="10"
              />
            </div>
            <div class="flex flex-col gap-4">
              <UploadFileImage
                title="Thẻ ảnh"
                v-model:refImg="refImgMeta"
                v-model:inputFile="inputFileMeta"
              >
                <template #preview>
                  <div class="border p-2 flex justify-center">
                    <ImageEmptyIcon
                      :class="inputFileMeta ? 'hidden' : ''"
                      class="text-gray-400 h-48"
                    ></ImageEmptyIcon>
                    <img
                      :class="!inputFileMeta ? 'hidden' : ''"
                      ref="refImgMeta"
                      class="h-48 w-full"
                      src=""
                      alt=""
                    />
                  </div>
                </template>
              </UploadFileImage>
            </div>
          </div>
        </div>
      </div>
    </div>
    <div class="flex p-4 border border-gray-300 rounded-sm gap-2 justify-end">
      <Button
        :variant="'subtle'"
        theme="gray"
        size="md"
        label="Hủy"
        route="/posts"
      ></Button>
      <Button :variant="'solid'" theme="blue" size="md" label="Lưu"></Button>
    </div>
  </div>
</template>

<script setup>
import AttachmentIcon from '@/components/Icons/AttachmentIcon.vue'
import ImageEmptyIcon from '@/components/Icons/ImageEmptyIcon.vue'
import LayoutHeader from '@/components/LayoutHeader.vue'
import UploadFileImage from '@/components/UploadFileImage.vue'
import { Breadcrumbs, FormControl, ErrorMessage } from 'frappe-ui'
import { ref, onMounted } from 'vue'

const breadcrumbs = [
  { label: 'Quản lý bài viết', route: { name: 'Posts' } },
  { label: 'Thêm mới bài viết', route: { name: 'Posts Create' } },
]

const inputValue = '2024-05-08'
const refImg = ref(null)
const refImgMeta = ref(null)
const inputFile = ref()
const inputFileMeta = ref()
const messageError = ref({})
const content = ref()
const autocompleteValue = ref()
</script>
