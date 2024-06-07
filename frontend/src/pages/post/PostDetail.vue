<template>
  <LayoutHeader>
    <template #left-header>
      <Breadcrumbs :items="breadcrumbs" />
    </template>
    <template #right-header>
      <div
        class="gap-2 justify-end"
        :class="alreadyActions ? 'flex' : 'hidden'"
      >
        <Dropdown
          :options="[
            {
              group: 'Xóa',
              items: [
                {
                  label: 'Xóa bài viết',
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
          label="Hủy"
          @click="post.reload()"
          :disabled="!dirty"
        ></Button>
        <Button
          variant="solid"
          theme="blue"
          size="md"
          label="Lưu"
          @click="callUpdateDoc"
          :disabled="!dirty"
        ></Button>
      </div>
    </template>
  </LayoutHeader>
  <div class="p-6 overflow-auto">
    <div v-if="msgError" class="p-4 border border-gray-300 rounded-sm mb-4">
      <div class="text-base text-red-600 font-bold mb-2">Có lỗi xảy ra:</div>
      <ErrorMessage :message="msgError" />
    </div>
    <div v-if="_post" class="p-6 border border-gray-300 rounded-sm mb-4">
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
    </div>
  </div>
  <Dialog
    :options="{
      title: 'Xóa bài viết',
      actions: [
        {
          label: 'Xóa',
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
          Bạn chắc chắn muốn xóa bài viết:
          <b>"{{ _post?.title }}"</b>?
        </div>
        <div class="text-base">
          <p>- <b class="text-red-600"> Không thể hoàn tác</b>.</p>
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
  ErrorMessage,
  call,
  createResource,
  Dropdown,
} from 'frappe-ui'
import { createToast, errorMessage, warningMessage } from '@/utils'
import { ref, computed, watch } from 'vue'
import { useRouter } from 'vue-router'
import { globalStore } from '@/stores/global'
const { changeLoadingValue } = globalStore()

const router = useRouter()
const props = defineProps({
  postId: {
    type: String,
    required: true,
  },
})
const msgError = ref()
let _post = ref({})
const showModalDelete = ref(false)

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
              name: 'upload_file_image',
              type: 'upload_image',
              imgPreview: 'meta_image',
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

const post = createResource({
  url: 'go1_cms.api.post.get_post',
  params: {
    name: props.postId,
  },
  auto: true,
  transform: (data) => {
    data.published = data.published == 1
    data.upload_file_image = null
    _post.value = {
      ...data,
    }
    return data
  },
})

// function removeDOMSInHtmlString(htmlString, classRm = '.ql-editor') {
//   if (!htmlString) return htmlString

//   const parser = new DOMParser()
//   const doc = parser.parseFromString(htmlString, 'text/html')
//   const editor = doc.querySelector(classRm)

//   if (editor) {
//     while (editor.firstChild) {
//       editor.parentNode.insertBefore(editor.firstChild, editor)
//     }
//     editor.remove()
//   }

//   return doc.body.innerHTML
// }

// handle allow actions
const alreadyActions = ref(false)
const dirty = computed(() => {
  return JSON.stringify(post.data) !== JSON.stringify(_post.value)
})

watch(dirty, (val) => {
  alreadyActions.value = true
})

// update doc
async function callUpdateDoc() {
  msgError.value = null
  let _post_cp = { ..._post.value }

  if (JSON.stringify(post.data) == JSON.stringify(_post_cp)) {
    warningMessage('Tài liệu không thay đổi')
    return
  }

  changeLoadingValue(true, 'Đang lưu...')
  try {
    if (_post.value['upload_file_image']) {
      let headers = { Accept: 'application/json' }
      if (window.csrf_token && window.csrf_token !== '{{ csrf_token }}') {
        headers['X-Frappe-CSRF-Token'] = window.csrf_token
      }

      let imgForm = new FormData()
      imgForm.append(
        'file',
        _post.value['upload_file_image'],
        _post.value['upload_file_image'].name
      )
      imgForm.append('is_private', 0)
      imgForm.append('doctype', 'Mbw Blog Post')
      imgForm.append('fieldname', 'meta_image')
      imgForm.append('docname', props.postId)
      imgForm.append('file_url_old', _post.value.meta_image)

      await fetch('/api/method/go1_cms.api.handler_file.upload_file', {
        headers: headers,
        method: 'POST',
        body: imgForm,
      })
        .then((res) => res.json())
        .then((data) => {
          if (data.message) {
            // update image doc
            _post.value['meta_image'] = data.message.file_url
          }
        })
        .catch((err) => {
          msgError.value = err.messages.join(', ')
        })
    }

    const docUpdate = await call('go1_cms.api.post.update_post', {
      data: { ..._post.value },
    })

    if (docUpdate.name) {
      post.reload()

      createToast({
        title: 'Cập nhật thành công',
        icon: 'check',
        iconClasses: 'text-green-600',
      })
    }
  } catch (err) {
    if (err.messages && err.messages.length) {
      msgError.value = err.messages.join(', ')
      errorMessage('Có lỗi xảy ra', err.messages.join(', '))
    } else {
      errorMessage('Có lỗi xảy ra', err)
    }
  }
  changeLoadingValue(false)
}

// delete doc
async function deleteDoc(close) {
  changeLoadingValue(true, 'Đang xóa...')
  try {
    await call('go1_cms.api.post.delete_post', {
      name: props.postId,
    }).then(() => {
      createToast({
        title: 'Xóa thành công',
        icon: 'check',
        iconClasses: 'text-green-600',
      })
      close()
      router.push({
        name: 'Posts',
      })
    })
  } catch (err) {
    if (err.messages && err.messages.length) {
      msgError.value = err.messages.join(', ')
      errorMessage('Có lỗi xảy ra', err.messages.join(', '))
    } else {
      errorMessage('Có lỗi xảy ra', err)
    }
  }
  changeLoadingValue(false)
}

// breadcrumbs
const breadcrumbs = computed(() => {
  let items = [{ label: 'Quản lý bài viết', route: { name: 'Posts' } }]
  items.push({
    label: post.data?.title,
    route: {},
  })
  return items
})
</script>
