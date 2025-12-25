<template>
  <div class="notification-alert-container space-y-3">
    <!-- Employee Check-in Alert -->
    <Alert v-if="checkInAlert.show"
      :title="`Continuous Check-ins`"
      :description="`Day ${checkInAlert.checkins} of consistent daily check-ins`"
      :dismissable="true"
      :theme="checkInAlert.leagueTheme">
      <!-- Progress bar showing continuous days -->
       <template #footer>
        <div class="col-span-full mt-2 flex flex-col items-center justify-center space-y-1">
          <div class="flex justify-between items-center w-full text-sm lg:text-lg text-gray-300">
            <span class="flex">{{ checkInAlert.checkins }} Day{{ checkInAlert.checkins > 1 ? 's' : '' }}</span>
              <Badge :variant="'subtle'"
              :theme="checkInAlert.leagueTheme"
              size="md"
              label="Badge">
                {{ checkInAlert.league }}
              </Badge>
          </div>
          <Progress :value="checkInAlert.progress" size="md"  />
        </div>
      </template>
    </Alert>

    <!-- Normal Notification Alert (from Global Resource) -->
    <Alert v-if="normalNotification.show" :title="normalNotification.title"
      :description="normalNotification.description" :dismissable="true" :theme="'green'">
      <template #footer>
        <div class="mt-2 col-span-full flex flex-col items-center gap-2">
          <router-link :to="{ name: 'Notifications' }" 
            class="text-xs font-medium w-full px-3 py-2 border-none rounded-lg
            hover:bg-yellow-100/25 flex items-center gap-1">
            <!-- <LucideBell class="h-4 w-4 text-yellow-700 hover:text-yellow-600" /> -->
            <span class="flex text-gray-300">
              View Notifications
            </span>
          </router-link>
        </div>
      </template>
    </Alert>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, computed, defineExpose, watch } from 'vue'
import { Progress, Badge } from 'frappe-ui'

import Alert from './Alert/Alert.vue'
import { unreadNotifications } from '@/data/notifications'
import { userCheckins } from '@/data/users'

/**
 * Configuration interface for normal notifications
 */
interface NotificationConfig {
  title?: string
  description?: string
  type?: 'success' | 'error' | 'warning' | 'info'
  actionText?: string
  onAction?: () => void
  currentTimer?: ReturnType<typeof setTimeout> | null
}

/**
 * Employee check-in event data structure from backend
 */
interface EmployeeCheckInEvent {
  employee: string
  continuousCheckinDays: number
  maxStreak?: number
}

/**
 * League configuration and theme mapping
 */
interface LeagueConfig {
  league: string
  theme: 'gray' | 'blue' | 'green' | 'orange' | 'yellow' | 'red'
  minDays: number
}

const LEAGUE_CONFIG: Record<number, LeagueConfig> = {
  0: { league: 'Bronze', theme: 'yellow', minDays: 0 },
  15: { league: 'Silver', theme: 'gray', minDays: 15 },
  45: { league: 'Gold', theme: 'orange', minDays: 45 },
  75: { league: 'Platinum', theme: 'blue', minDays: 75 },
  100: { league: 'Diamond', theme: 'green', minDays: 100 },
} as const

/**
 * ============================================================================
 * NotificationAlert Component
 * ============================================================================
 * 
 * PURPOSE:
 * Displays two types of notifications in a unified, reusable component:
 * 1. Employee Check-in Progress: Real-time WebSocket events showing continuous
 *    check-in streaks with visual progress indicators
 * 2. Normal Notifications: Traditional app notifications from the global
 *    'Unread Notifications Count' resource
 * 
 * ============================================================================
 */

// ─────────────────────────────────────────────────────────────────────────
// STATE: Employee Check-in Alerts
// ─────────────────────────────────────────────────────────────────────────
/**
 * Reactive state for check-in progress alerts
 * - show: Whether alert is visible
 * - employeeName: Name of employee with streak
 * - progress: Current streak day / progress percentage (0-100)
 * - currentTimer: Reference to timeout for auto-hide
 */
const checkInAlert = ref({
  show: false,
  employeeName: '',
  progress: 0,
  checkins: 0,
  league: '',
  leagueTheme: 'gray' as "gray" | "blue" | "green" | "yellow" | "orange" | "red",

  currentTimer: null as ReturnType<typeof setTimeout> | null,
})

// ─────────────────────────────────────────────────────────────────────────
// STATE: Normal Notifications
// ─────────────────────────────────────────────────────────────────────────
/**
 * Reactive state for traditional app notifications
 * - show: Whether alert is visible
 * - title: Notification title
 * - description: Notification body text
 * - type: Alert variant (success, error, warning, info)
 * - actionText: Optional button text for CTA
 * - onAction: Callback when action button clicked
 */
const normalNotification = ref<NotificationConfig & { show: boolean; onAction?: () => void }>({
  show: false,
  title: 'New Notification',
  description: 'You have a new notification',
  type: 'info',
  actionText: '',
  onAction: undefined,
  currentTimer: null as ReturnType<typeof setTimeout> | null,
})

// ─────────────────────────────────────────────────────────────────────────
// METHODS: Check-in Alert Handlers
// ─────────────────────────────────────────────────────────────────────────
/**
 * Determine current league based on continuous check-in days
 * Returns the league config for the current milestone
 */
const getCurrentLeague = (days: number): LeagueConfig => {
  if (days >= 100) return LEAGUE_CONFIG[100]
  if (days >= 75) return LEAGUE_CONFIG[75]
  if (days >= 45) return LEAGUE_CONFIG[45]
  if (days >= 15) return LEAGUE_CONFIG[15]
  return LEAGUE_CONFIG[0]
}

/**
 * Calculate the next league threshold
 */
const getNextLeagueThreshold = (days: number): number => {
  const current = getCurrentLeague(days)
  const thresholds = [15, 45, 75, 100]
  const next = thresholds.find(t => t > current.minDays)
  return next || 100
}

/**
 * Validate employee check-in event data
 * Returns true if data is valid, false otherwise
 */
const isValidCheckInEvent = (data: any): data is EmployeeCheckInEvent => {
  if (!data) return false
  if (typeof data.employee !== 'string') {
    console.warn('[NotificationAlert] Invalid check-in event: employee must be a string', data)
    return false
  }
  if (typeof data.continuousCheckinDays !== 'number' || data.continuousCheckinDays < 0) {
    console.warn('[NotificationAlert] Invalid check-in event: continuousCheckinDays must be a positive number', data)
    return false
  }
  return true
}

/**
 * Handle employee check-in with validation
 * 
 * DATA STRUCTURE (from backend):
 * {
 *   employee: "John Doe",           // Employee Display Name
 *   continuousCheckinDays: 15,     // Total consecutive check-in days
 *   maxStreak: 30                  // (optional) Max possible streak
 * }
 */
const handleCheckInEvent = (data: any) => {
  try {
    // Validate event data
    if (!isValidCheckInEvent(data)) {
      return
    }

    // Clear any existing auto-hide timer
    if (checkInAlert.value.currentTimer) {
      clearTimeout(checkInAlert.value.currentTimer)
    }

    // Calculate current league and next threshold
    const currentLeague = getCurrentLeague(data.continuousCheckinDays)
    const nextThreshold = getNextLeagueThreshold(data.continuousCheckinDays)
    const progressPercent = Math.min(
      (data.continuousCheckinDays / nextThreshold) * 100,
      100
    )

    // Update alert state
    checkInAlert.value = {
      show: true,
      employeeName: data.employee,
      progress: Math.round(progressPercent),
      checkins: data.continuousCheckinDays,
      league: currentLeague.league,
      leagueTheme: currentLeague.theme,
      currentTimer: null,
    }

    // Auto-hide on completion
    if (progressPercent >= 100) {
      checkInAlert.value.currentTimer = setTimeout(() => {
        closeCheckInAlert()
      }, 7000)
    } else {
      // Auto-hide after 8 seconds if not complete _-_
      checkInAlert.value.currentTimer = setTimeout(() => {
        closeCheckInAlert()
      }, 7000)
    }
  } catch (error) {
    console.error('[NotificationAlert] Error handling check-in event:', error)
  }
}

/**
 * Close check-in alert and clear timer
 */
const closeCheckInAlert = () => {
  if (checkInAlert.value.currentTimer) {
    clearTimeout(checkInAlert.value.currentTimer)
  }
  checkInAlert.value = {
    show: false,
    employeeName: '',
    progress: 0,
    league: '',
    leagueTheme: 'gray',
    currentTimer: null,
  }
}

// ─────────────────────────────────────────────────────────────────────────
// METHODS: Normal Notification Handlers
// ─────────────────────────────────────────────────────────────────────────
/**
 * Display a normal notification alert
 * 
 * USAGE:
 * showNormalNotification({
 *   title: "Task Updated",
 *   description: "Your task has been assigned",
 *   type: "success",
 *   actionText: "View",
 *   onAction: () => { console.log('Action clicked') }
 * })
 */
const showNormalNotification = (config: NotificationConfig) => {
  if (normalNotification.value.currentTimer) {
    clearTimeout(normalNotification.value.currentTimer)
  }
  normalNotification.value = {
    show: true,
    title: config.title || 'Notification',
    description: config.description || '',
    type: config.type || 'info',
    actionText: config.actionText || '',
    onAction: config.onAction,
  }
  normalNotification.value.currentTimer = setTimeout(() => {
    closeNormalAlert()
  }, 5000) // Auto-hide after 5 seconds
}

/**
 * Close normal notification alert
 */
const closeNormalAlert = () => {
  normalNotification.value = {
    show: false,
    title: '',
    description: '',
    type: 'info',
    actionText: '',
  }
}

/**
 * Handle notification action button click
 * Calls the onAction callback if provided
 */
const handleNotificationAction = () => {
  try {
    if (normalNotification.value.onAction && typeof normalNotification.value.onAction === 'function') {
      normalNotification.value.onAction()
    }
  } catch (error) {
    console.error('[NotificationAlert] Error in notification action handler:', error)
  } finally {
    closeNormalAlert()
  }
}

// ─────────────────────────────────────────────────────────────────────────
// REACTIVE WATCHERS
// ─────────────────────────────────────────────────────────────────────────
/**
 * Watch for changes in unread notifications count
 * Shows alert when new unread notifications arrive
 */
watch(
  unreadNotifications.data,
  (notificationCount) => {

    if (notificationCount > 0 && !normalNotification.value.show) {
      const count = notificationCount as number
      showNormalNotification({
        title: 'New Notifications',
        description: count > 0 ? `You have ${count} unread notification${count !== 1 ? 's' : ''}` : 'New notification arrived',
        type: 'info',
        actionText: 'View',
      })
    }
  },
  { immediate: true }
)

// ─────────────────────────────────────────────────────────────────────────
// LIFECYCLE HOOKS
// ─────────────────────────────────────────────────────────────────────────
/**
 * Setup WebSocket listeners when component mounts
 */
onMounted(() => {
  // retrieve employee check-in events from backend
  userCheckins.execute().then((d:EmployeeCheckInEvent) => {
    handleCheckInEvent(d)
  }).catch((err:any) => {
    console.error('[NotificationAlert] Error fetching user check-in data:', err)
  })
})

/**
 * Cleanup: Remove WebSocket listeners when component unmounts
 * CRITICAL: Prevents memory leaks and duplicate listeners
 */
onUnmounted(() => {
  // Clear any pending timers
  if (checkInAlert.value.currentTimer) {
    clearTimeout(checkInAlert.value.currentTimer)
  }
  if (normalNotification.value.currentTimer) {
    clearTimeout(normalNotification.value.currentTimer)
  }

  // Close any open notifications
  closeNormalAlert()
  closeCheckInAlert()
})

// ─────────────────────────────────────────────────────────────────────────
// EXPOSE PUBLIC METHODS
// ─────────────────────────────────────────────────────────────────────────
/**
 * Make methods available to parent components via template ref
 * Example in parent: this.$refs.notificationAlert.showNormalNotification(...)
 */
defineExpose({
  showNormalNotification,
  closeNormalAlert,
})
</script>

<style scoped>
/**
 * Component-scoped styles for notification alerts
 * Mobile-friendly: prevents horizontal scroll and ensures proper spacing
 */
.notification-alert-container {
  position: fixed;
  top: 1rem;
  left: 0;
  right: 0;
  z-index: 1000;
  height: auto;
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  align-items: center;
  gap: 0.75rem;
  pointer-events: none;
  padding: 0 1rem;
}

/* Allow pointer events only on child alerts */
.notification-alert-container > * {
  pointer-events: auto;
  max-width: 90vw;
  width: 100%;
}

@media (min-width: 640px) {
  .notification-alert-container > * {
    max-width: 500px;
  }
}
</style>