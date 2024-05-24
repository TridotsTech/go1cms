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
            variant="subtle"
            theme="gray"
            size="md"
            label="Hủy"
            route="/posts"
          ></Button>
          <Button
            variant="solid"
            theme="blue"
            size="md"
            label="Lưu"
            @click="callInsertDoc"
          ></Button>
        </div>
      </div>
    </div>
    <div class="p-6 border border-gray-300 rounded-sm mb-4">
      <div>
        <div class="mb-4">
          <h2 class="font-bold text-xl">Thông tin cơ bản</h2>
        </div>
        <div class="mb-5">
          <Fields :sections="sections" :data="_post" />
        </div>
      </div>
      <div class="mt-2 mb-5 border-t">
        <div class="my-4">
          <h2 class="font-bold text-xl">SEO</h2>
        </div>
        <div class="mb-5">
          <Fields :sections="sections1" :data="_post" />
        </div>
      </div>
      <div class="border-t border-gray-300">
        <ErrorMessage class="mt-3" :message="msgError" />
        <div class="flex py-4 gap-2 justify-end">
          <Button
            variant="subtle"
            theme="gray"
            size="md"
            label="Hủy"
            route="/posts"
          ></Button>
          <Button
            variant="solid"
            theme="blue"
            size="md"
            label="Lưu"
            @click="callInsertDoc"
          ></Button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import Fields from '@/components/Fields.vue'
import LayoutHeader from '@/components/LayoutHeader.vue'
import { Breadcrumbs, ErrorMessage, call, createResource } from 'frappe-ui'
import { createToast, errorMessage } from '@/utils'
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { globalStore } from '@/stores/global'
const { changeLoadingValue } = globalStore()

const router = useRouter()
const breadcrumbs = [
  { label: 'Quản lý bài viết', route: { name: 'Posts' } },
  { label: 'Thêm mới bài viết', route: { name: 'Post Create' } },
]

let _post = ref({})
const msgError = ref()

const sections = computed(() => {
  return [
    {
      section: 'post-1',
      columns: 1,
      class: 'md:grid-cols-2',
      fields: [
        {
          label: 'Tên bài viết',
          mandatory: true,
          name: 'title',
          type: 'data',
          placeholder: 'Nhập tên bài viết',
        },
        {
          label: 'Ẩn / Hiển thị bài viết',
          labelInput: 'Hiển thị',
          name: 'published',
          type: 'checkbox',
        },
        {
          section: 'post-1-1',
          typeArray: true,
          fields: [
            {
              label: 'Danh mục',
              mandatory: true,
              name: 'blog_category',
              type: 'link',
              placeholder: 'Chọn danh mục',
              doctype: 'Mbw Blog Category',
            },
            {
              label: 'Giới thiệu bài viết',
              name: 'blog_intro',
              type: 'textarea',
              placeholder: 'Nhập giới thiệu',
              rows: 10,
            },
          ],
        },
        {
          section: 'post-1-2',
          typeArray: true,
          fields: [
            {
              label: 'Ngày đăng (Mặc định sẽ tự tạo khi hiển thị)',
              name: 'published_on',
              type: 'date',
              placeholder: 'dd/mm/yyyy',
            },
            {
              label: 'Đường dẫn (Mặc định sẽ tự tạo)',
              name: 'route',
              type: 'data',
              placeholder: 'Nhập đường dẫn',
            },

            {
              label: 'Ảnh',
              name: 'file_image',
              type: 'upload_image',
            },
          ],
        },
      ],
    },
    {
      section: 'post-2',
      columns: 1,
      class: 'md:grid-cols-1',
      hideBorder: true,
      fields: [
        {
          label: 'Nội dung bài viết',
          name: 'content',
          type: 'texeditor',
          placeholder: 'Nhập nội dung',
        },
      ],
    },
  ]
})

const sections1 = computed(() => {
  return [
    {
      section: 'post-3',
      columns: 1,
      class: 'md:grid-cols-2',
      fields: [
        {
          label: 'Thẻ tiêu đề',
          name: 'meta_title',
          type: 'data',
          placeholder: 'Nhập thẻ tiêu đề',
        },
      ],
    },
    {
      section: 'post-4',
      columns: 1,
      class: 'md:grid-cols-2',
      hideBorder: true,
      fields: [
        {
          label: 'Thẻ từ khóa',
          name: 'meta_keywords',
          type: 'textarea',
          placeholder: 'Nhập thẻ từ khóa',
          rows: 10,
        },
        {
          label: 'Thẻ mô tả',
          name: 'meta_description',
          type: 'textarea',
          placeholder: 'Nhập thẻ mô tả',
          rows: 10,
        },
      ],
    },
  ]
})

async function callInsertDoc() {
  changeLoadingValue(true, 'Đang lưu...')
  try {
    const docCreate = await call('go1_cms.api.post.create_post', {
      data: { ..._post.value },
    })

    if (docCreate.name && _post.value['file_image']) {
      let headers = { Accept: 'application/json' }
      if (window.csrf_token && window.csrf_token !== '{{ csrf_token }}') {
        headers['X-Frappe-CSRF-Token'] = window.csrf_token
      }

      let imgForm = new FormData()
      imgForm.append(
        'file',
        _post.value['file_image'],
        _post.value['file_image'].name
      )
      imgForm.append('is_private', '0')
      imgForm.append('doctype', 'Mbw Blog Post')
      imgForm.append('fieldname', 'meta_image')
      imgForm.append('docname', docCreate.name)

      let imgres = await fetch('/api/method/upload_file', {
        headers: headers,
        method: 'POST',
        body: imgForm,
      })
        .then((res) => res.json())
        .then(async (data) => {
          if (data.message) {
            // update image doc
            await call('frappe.client.set_value', {
              doctype: 'Mbw Blog Post',
              name: docCreate.name,
              fieldname: 'meta_image',
              value: data.message.file_url || '',
            })
          }
        })
    }

    createToast({
      title: 'Thêm mới thành công',
      icon: 'check',
      iconClasses: 'text-green-600',
    })
    docCreate.name &&
      router.push({
        name: 'Post Detail',
        params: { postId: docCreate.name },
      })
  } catch (err) {
    msgError.value = err.messages.join(', ')
    errorMessage('Có lỗi xảy ra', err.messages.join(', '))
  }
  changeLoadingValue(false)
}
</script>
