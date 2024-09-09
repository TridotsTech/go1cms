<template>
  <div
    class="relative flex h-full flex-col justify-between transition-all duration-300 ease-in-out"
    :class="isSidebarCollapsed ? 'w-15' : 'w-56'"
  >
    <div class="flex justify-center border-b">
      <UserDropdown class="p-2" :isCollapsed="isSidebarCollapsed" />
    </div>
    <div class="flex-1 overflow-y-auto pt-2">
      <!-- <div class="mb-3 flex flex-col">
        <SidebarLink
          id="notifications-btn"
          label="Notifications"
          :icon="NotificationsIcon"
          :isCollapsed="isSidebarCollapsed"
          @click="() => toggleNotificationPanel()"
          class="relative mx-2 my-0.5"
        >
          <template #right>
            <Badge
              v-if="
                !isSidebarCollapsed &&
                notificationsStore().unreadNotificationsCount
              "
              :label="notificationsStore().unreadNotificationsCount"
              variant="subtle"
            />
            <div
              v-else-if="notificationsStore().unreadNotificationsCount"
              class="absolute -left-1.5 top-1 z-20 h-[5px] w-[5px] translate-x-6 translate-y-1 rounded-full bg-gray-800 ring-1 ring-white"
            ></div>
          </template>
        </SidebarLink>
      </div> -->
      <div
        v-if="!isSidebarCollapsed && name_website_edit"
        class="m-2 text-base p-2 rounded-md border-2 bg-gray-200"
      >
        <p class="text-gray-700 font-bold">{{ name_website_edit }}</p>
      </div>
      <div v-for="view in allViews" :key="view.label">
        <div
          v-if="!view.hideLabel && isSidebarCollapsed && view.views?.length"
          class="mx-2 my-2 h-1 border-b"
        ></div>
        <Section
          :label="view.name"
          :hideLabel="view.hideLabel"
          :isOpened="view.opened"
        >
          <template #header="{ opened, hide, toggle }">
            <div
              v-if="!hide"
              class="flex justify-between cursor-pointer gap-1.5 px-3 text-sm font-medium text-gray-600 transition-all duration-300 ease-in-out"
              :class="
                isSidebarCollapsed
                  ? 'ml-0 h-0 overflow-hidden opacity-0'
                  : 'ml-2 mt-4 h-7 w-auto opacity-100'
              "
              @click="toggle()"
            >
              <div class="flex gap-1.5">
                <component :is="view.icon" class="h-4 w-4 text-gray-700" />
                <span class="uppercase">
                  {{ view.name }}
                </span>
              </div>
              <FeatherIcon
                name="chevron-right"
                class="h-4 text-gray-900 transition-all duration-300 ease-in-out"
                :class="{ 'rotate-90': opened }"
              />
            </div>
          </template>
          <nav class="flex flex-col">
            <SidebarLink
              v-for="link in view.views"
              :icon="link.icon"
              :label="link.label"
              :to="link.to"
              :isCollapsed="isSidebarCollapsed"
              class="mx-2 my-0.5"
            />
          </nav>
        </Section>
      </div>
    </div>
    <div class="m-2 flex flex-col gap-1">
      <SidebarLink
        label="Tài liệu"
        :isCollapsed="isSidebarCollapsed"
        icon="book-open"
        @click="() => openDocs()"
      />
      <SidebarLink
        :label="isSidebarCollapsed ? 'Mở rộng' : 'Thu nhỏ'"
        :isCollapsed="isSidebarCollapsed"
        @click="isSidebarCollapsed = !isSidebarCollapsed"
        class=""
      >
        <template #icon>
          <span class="grid h-5 w-6 flex-shrink-0 place-items-center">
            <CollapseSidebar
              class="h-4.5 w-4.5 text-gray-700 duration-300 ease-in-out"
              :class="{ '[transform:rotateY(180deg)]': isSidebarCollapsed }"
            />
          </span>
        </template>
      </SidebarLink>
    </div>
    <!-- <Notifications /> -->
  </div>
</template>

<script setup>
import Section from '@/components/Section.vue'
import FormSetupIcon from '@/components/Icons/FormSetupIcon.vue'
import NewsIcon from '@/components/Icons/NewsIcon.vue'
import TemplatePageIcon from '@/components/Icons/TemplatePageIcon.vue'
import WebpageIcon from '@/components/Icons/WebpageIcon.vue'
import MyWebsiteIcon from '@/components/Icons/MyWebsiteIcon.vue'
import DomainIcon from '@/components/Icons/DomainIcon.vue'
import DisplayIcon from '@/components/Icons/DisplayIcon.vue'
import HeaderIcon from '@/components/Icons/HeaderIcon.vue'
import FooterIcon from '@/components/Icons/FooterIcon.vue'
import HomeIcon from '@/components/Icons/HomeIcon.vue'
import ServiceIcon from '@/components/Icons/ServiceIcon.vue'
import NewPageIcon from '@/components/Icons/NewPageIcon.vue'
import PostIcon from '@/components/Icons/PostIcon.vue'
import FormIcon from '@/components/Icons/FormIcon.vue'
import DescriptionIcon from '@/components/Icons/DescriptionIcon.vue'
import PinIcon from '@/components/Icons/PinIcon.vue'
import ChartIcon from '@/components/Icons/ChartIcon.vue'
import UserDropdown from '@/components/UserDropdown.vue'
import PolicyIconV1 from '@/components/Icons/PolicyIconV1.vue'
import ContactsIcon from '@/components/Icons/ContactsIcon.vue'
import ContactsIconV1 from '@/components/Icons/ContactsIconV1.vue'
import OrganizationsIcon from '@/components/Icons/OrganizationsIcon.vue'
import SettingsIcon from '@/components/Icons/SettingsIcon.vue'
import MenuIcon from '@/components/Icons/MenuIcon.vue'
import CollapseSidebar from '@/components/Icons/CollapseSidebar.vue'
import NotificationsIcon from '@/components/Icons/NotificationsIcon.vue'
import SidebarLink from '@/components/SidebarLink.vue'
import Notifications from '@/components/Notifications.vue'
import { viewsStore } from '@/stores/views'
import { notificationsStore } from '@/stores/notifications'
import { FeatherIcon } from 'frappe-ui'
import { useStorage } from '@vueuse/core'
import { computed } from 'vue'
import { storeToRefs } from 'pinia'
import { globalStore } from '@/stores/global'
const { changeNameWebsiteEdit } = globalStore()
const { name_website_edit } = storeToRefs(globalStore())

const { views } = viewsStore()

const isSidebarCollapsed = useStorage('isSidebarCollapsed', false)

const links = [
  // {
  //   label: 'Website của tôi',
  //   icon: MyWebsiteIcon,
  //   to: 'My Website',
  // },
  {
    label: 'Kho giao diện',
    icon: DisplayIcon,
    to: 'Interface Repository',
  },
]

const allViews = computed(() => {
  let _views = [
    {
      name: 'Publish',
      hideLabel: true,
      opened: true,
      views: links,
    },
  ]

  if (views.data?.website_primary == 1) {
    changeNameWebsiteEdit(views.data?.name_web)
    //
    _views.push({
      name: 'Bảng chính',
      opened: true,
      views: [
        {
          label: 'Dashboard',
          icon: ChartIcon,
          to: 'Dashboard',
        },
      ],
    })

    //
    _views.push({
      name: 'Cấu hình chung',
      opened: true,
      // icon: SettingsIcon,
      views: [
        {
          label: 'Menu',
          icon: MenuIcon,
          to: 'Menu',
        },
        {
          label: 'Domain',
          icon: DomainIcon,
          to: 'Domain',
        },

        {
          label: 'Thiết lập website',
          icon: SettingsIcon,
          to: 'Website Setup',
        },
        {
          label: 'Cấu hình biểu mẫu',
          icon: FormSetupIcon,
          to: 'Form Setup',
        },
      ],
    })

    if (views.data?.list_page) {
      let items_view = [
        {
          label: 'Đầu trang',
          icon: HeaderIcon,
          to: 'Header Page',
        },
        {
          label: 'Chân trang',
          icon: FooterIcon,
          to: 'Footer Page',
        },
      ]
      views.data?.list_page.forEach((el) => {
        items_view.push({
          label: el.name_page,
          icon: getIcon(el.icon),
          to: {
            name: 'Page',
            query: { view: el.name },
          },
        })
      })
      items_view.push({
        label: 'Thêm trang mới',
        icon: NewPageIcon,
        to: 'New Page',
      })

      _views.push({
        name: 'Danh sách trang',
        opened: true,
        // icon: InboxIcon,
        views: items_view,
      })
    }

    //
    _views.push({
      name: 'Bài viết & biểu mẫu',
      opened: true,
      // icon: InboxIcon,
      views: [
        {
          label: 'Quản lý bài viết',
          icon: PostIcon,
          to: 'Posts',
        },
        {
          label: 'Quản lý biểu mẫu',
          icon: FormIcon,
          to: 'Forms',
        },
        {
          label: 'Danh sách liên hệ',
          icon: ContactsIconV1,
          to: 'Contacts',
        },
      ],
    })
  }

  // if (views.data?.developer_mode == 1) {
  //   _views.push({
  //     name: 'Tạo tệp Json website mẫu',
  //     opened: true,
  //     views: [
  //       {
  //         label: 'Trình tạo',
  //         icon: JsonIcon,
  //         to: 'Setup File Template',
  //       },
  //     ],
  //   })
  // }

  return _views
})

function parseView(views) {
  return views.map((view) => {
    return {
      label: view.label,
      icon: getIcon(view.route_name),
      to: {
        name: view.route_name,
        query: { view: view.name },
      },
    }
  })
}

function getIcon(name) {
  switch (name) {
    case 'PolicyIconV1':
      return PolicyIconV1
    case 'WebpageIcon':
      return WebpageIcon
    case 'TemplatePageIcon':
      return TemplatePageIcon
    case 'HeaderIcon':
      return HeaderIcon
    case 'FooterIcon':
      return FooterIcon
    case 'HomeIcon':
      return HomeIcon
    case 'OrganizationsIcon':
      return OrganizationsIcon
    case 'ServiceIcon':
      return ServiceIcon
    case 'NewPageIcon':
      return NewPageIcon
    case 'NewsIcon':
      return NewsIcon
    case 'ContactsIcon':
      return ContactsIcon
    case 'DescriptionIcon':
      return DescriptionIcon
    default:
      return PinIcon
  }
}

function openDocs() {
  window.open('#', '_blank')
}
</script>
