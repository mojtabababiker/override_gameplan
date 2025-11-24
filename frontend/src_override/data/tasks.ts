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
    // wrap the useDoc call, to intercept the calls for `update`, and`delete` to sync between GP and Frappe
    const useDocWrapper = useDoc<Task, TaskMethods>({
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
    const orgSetValueSubmit = useDocWrapper.setValue.submit
    const orgDeleteSubmit = useDocWrapper.delete.submit
    useDocWrapper.setValue.submit = async (doc) => {
      // call the original setValue
      await orgSetValueSubmit(doc)
      // After successfully updating the GP Task, call the updateProjectTask API to sync with Frappe
      const ogDoc = useDocWrapper.doc
      if (!ogDoc) return
      // console.log('Updating project task for GP Task:', name)
      // console.dir(ogDoc)
      await updateProjectTask.submit({ ...ogDoc, ...doc })
    }
    useDocWrapper.delete.submit = async () => {
      // call the original delete
      await orgDeleteSubmit()
      // After deleteing the GP Task, delete the corresponding Project Task in Frappe
      // console.log('Deleting project task for GP Task:', name)
      await deleteProjectTask.submit({ title: useDocWrapper.doc?.title, name: name })
    }
    tasksCache[name] = useDocWrapper
  }
  return tasksCache[name] as ReturnType<typeof useDoc<Task, TaskMethods>>
}

export const createProjectTask = useCall<any, GPTask>({
  method: 'POST',
  url: '/api/v2/method/override_gameplan.api.task.create_project_task_from_gp_task',
  immediate: true,
})

export const updateProjectTask = useCall<any, GPTask>({
  method: 'PUT',
  url: '/api/v2/method/override_gameplan.api.task.update_project_task_from_gp_task',
  immediate: true,
})

export const deleteProjectTask = useCall<any, { title?: string; name: string }>({
  method: 'PUT',
  url: '/api/v2/method/override_gameplan.api.task.delete_project_task_from_gp_task',
  immediate: true,
})
