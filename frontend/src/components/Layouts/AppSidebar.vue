<template>
  <div
    class="relative flex h-full flex-col justify-between transition-all duration-300 ease-in-out"
    :class="isSidebarCollapsed ? 'w-12' : 'w-56'"
  >
    <div>
      <UserDropdown class="p-2" :isCollapsed="isSidebarCollapsed" />
    </div>
    <div class="flex-1 overflow-y-auto">
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
        label="Docs"
        :isCollapsed="isSidebarCollapsed"
        icon="book-open"
        @click="() => openDocs()"
      />
      <SidebarLink
        :label="isSidebarCollapsed ? 'Expand' : 'Collapse'"
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
    <Notifications />
  </div>
</template>

<script setup>
import Section from '@/components/Section.vue'
import DashboardIcon from '@/components/Icons/DashboardIcon.vue'
import InboxIcon from '@/components/Icons/InboxIcon.vue'
import PolicyIcon from '@/components/Icons/PolicyIcon.vue'
import NewsIcon from '@/components/Icons/NewsIcon.vue'
import ProductIcon from '@/components/Icons/ProductIcon.vue'
import TemplateWebsiteIcon from '@/components/Icons/TemplateWebsiteIcon.vue'
import ArrowUpRightIcon from '@/components/Icons/ArrowUpRightIcon.vue'
import PinIcon from '@/components/Icons/PinIcon.vue'
import ChartIcon from '@/components/Icons/ChartIcon.vue'
import UserDropdown from '@/components/UserDropdown.vue'
import LeadsIcon from '@/components/Icons/LeadsIcon.vue'
import DealsIcon from '@/components/Icons/DealsIcon.vue'
import ContactsIcon from '@/components/Icons/ContactsIcon.vue'
import OrganizationsIcon from '@/components/Icons/OrganizationsIcon.vue'
import NoteIcon from '@/components/Icons/NoteIcon.vue'
import SettingsIcon from '@/components/Icons/SettingsIcon.vue'
import PhoneIcon from '@/components/Icons/PhoneIcon.vue'
import CollapseSidebar from '@/components/Icons/CollapseSidebar.vue'
import NotificationsIcon from '@/components/Icons/NotificationsIcon.vue'
import SidebarLink from '@/components/SidebarLink.vue'
import Notifications from '@/components/Notifications.vue'
import { viewsStore } from '@/stores/views'
import { notificationsStore } from '@/stores/notifications'
import { FeatherIcon } from 'frappe-ui'
import { useStorage } from '@vueuse/core'
import { computed } from 'vue'

const { getPinnedViews, getPublicViews } = viewsStore()
const { toggle: toggleNotificationPanel } = notificationsStore()

const isSidebarCollapsed = useStorage('isSidebarCollapsed', false)

const links = [
  {
    label: 'Dashboard',
    icon: ChartIcon,
    to: 'Dashboard',
  },
]

const allViews = computed(() => {
  let _views = [
    {
      name: 'All Views',
      hideLabel: true,
      opened: true,
      views: links,
    },
  ]

  //
  _views.push({
    name: 'Cấu hình',
    opened: true,
    icon: SettingsIcon,
    views: [
      {
        label: 'Chọn mẫu website',
        icon: TemplateWebsiteIcon,
        to: 'Email Templates',
      },
      {
        label: 'Cấu hình website',
        icon: ArrowUpRightIcon,
        to: 'Email Templates',
      },
    ],
  })

  //
  _views.push({
    name: 'Danh sách trang',
    opened: true,
    icon: InboxIcon,
    views: [
      {
        label: 'Trang chủ',
        icon: DashboardIcon,
        to: 'Email Templates',
      },
      {
        label: 'Giới thiệu công ty',
        icon: OrganizationsIcon,
        to: 'Email Templates',
      },
      {
        label: 'Tin tức',
        icon: NewsIcon,
        to: 'Email Templates',
      },
      {
        label: 'Chính sách bán hàng',
        icon: PolicyIcon,
        to: 'Email Templates',
      },
      {
        label: 'Sản phẩm bán hàng',
        icon: ProductIcon,
        to: 'Email Templates',
      },
      {
        label: 'Tuyển dụng',
        icon: DealsIcon,
        to: 'Email Templates',
      },
    ],
  })

  if (getPublicViews().length) {
    _views.push({
      name: 'Public views',
      opened: true,
      views: parseView(getPublicViews()),
    })
  }

  if (getPinnedViews().length) {
    _views.push({
      name: 'Pinned views',
      opened: true,
      views: parseView(getPinnedViews()),
    })
  }
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

function getIcon(routeName) {
  switch (routeName) {
    case 'Leads':
      return LeadsIcon
    case 'Deals':
      return DealsIcon
    case 'Contacts':
      return ContactsIcon
    case 'Organizations':
      return OrganizationsIcon
    case 'Notes':
      return NoteIcon
    case 'Call Logs':
      return PhoneIcon
    default:
      return PinIcon
  }
}

function openDocs() {
  window.open('https://docs.frappe.io/crm', '_blank')
}
</script>
