import {DateTime} from 'luxon'
import {filter, get, includes, intersectionWith, some} from 'lodash'
import {useDepartmentStore} from './department-edit-session'


const $_isInvalid = (e: any, evaluationIds: number[], fields: any) => {
  return includes(evaluationIds, e.id) && !(
    (e.departmentForm || get(fields, 'departmentFormId')) &&
    (e.evaluationType || get(fields, 'evaluationTypeId')) &&
    (e.instructor || get(fields, 'instructorUid'))
  )
}

export function validateConfirmable(evaluationIds: number[], fields: any) {
  if (some(useDepartmentStore().evaluations, e => $_isInvalid(e, evaluationIds, fields))) {
    useDepartmentStore().showErrorDialog('Cannot confirm evaluations with missing fields.')
    return false
  }
  return true
}

export function validateDuplicable(evaluationIds: number[], fields: any) {
  if (fields.midterm === 'true') {
    return true
  }
  const duplicatingEvaluations = filter(useDepartmentStore().evaluations, e => includes(evaluationIds, e.id))
  const conflicts = intersectionWith(duplicatingEvaluations, useDepartmentStore().evaluations, (dupe, e) => {
    return e.courseNumber === dupe.courseNumber &&
      get(e.instructor, 'uid', NaN) === (fields.instructorUid || get(dupe.instructor, 'uid', NaN))
  })
  if (conflicts.length) {
    useDepartmentStore().showErrorDialog('Cannot create identical duplicate evaluations.')
    return false
  }
  return true
}

export function validateMarkAsDone(selectedEvaluations: any[]): string | undefined {
  let warningMessage: string | undefined = undefined
  const evaluationsInProgress = filter(selectedEvaluations, e => DateTime.now() > DateTime.fromJSDate(e.startDate))
  if (evaluationsInProgress.length) {
    // Grab the first in-progress evaluation, to give the user an example of the problem.
    const e = evaluationsInProgress[0]
    const course = `${e.subjectArea} ${e.catalogId} ${e.instructionFormat} ${e.sectionNumber}`
    const startDate: any = DateTime.fromJSDate(e.startDate).toFormat('MM/dd/yy')
    if (evaluationsInProgress.length === 1) {
      warningMessage = `The ${course} evaluation period started on ${startDate}.
        Are you sure you want to mark it as done?`
    } else {
      warningMessage = `Some of the selected evaluation periods have already started.
        For example, ${course} evaluation period started on ${startDate}.
        Are you sure you want to mark those as done?`
    }
  }
  return warningMessage
}
