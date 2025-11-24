import { MaybeRefOrGetter, toValue } from 'vue'
import { useCall, useDoc } from 'frappe-ui/src/data-fetching'
import { GPTask } from '@/types/doctypes'

let tasksCache: Record<string, ReturnType<typeof useDoc>> = {}

export function useTask(taskId: MaybeRefOrGetter<string>) {
  interface Task extends GPTask {}

  interface TaskMethods {
    trackVisit: () => void
  }

  let name = toValue(taskId)
  if (!tasksCache[name]) {
    tasksCache[name] = useDoc<Task, TaskMethods>({
      doctype: 'GP Task',
      name: taskId,
      methods: {
        trackVisit: 'track_visit',
      },
      transform(doc) {
        return {
          ...doc,
          project: doc.project ? String(doc.project) : undefined,
        }
      },
    })
  }
  return tasksCache[name] as ReturnType<typeof useDoc<Task, TaskMethods>>
}

export const createProjectTask = useCall<any, GPTask>({
  method: 'POST',
  url: '/api/v2/method/override_gameplan.api.task.create_project_task_from_gp_task',
  immediate: true,
})

export const updateProjectTask = useCall<any, GPTask>({
  method: 'POST',
  url: '/api/v2/method/override_gameplan.api.task.update_project_task_from_gp_task',
  immediate: true,
})
