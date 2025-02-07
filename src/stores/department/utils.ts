import {DateTime} from 'luxon'
import {each, filter, get, includes, intersectionWith, some} from 'lodash'
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
  const evaluationsEnded = []
  each(selectedEvaluations, e => {
    let startDate
    if (DateTime.isDateTime(e.startDate)) {
      startDate = e.startDate
    } else if (e.startDate instanceof Date) {
      startDate = DateTime.fromJSDate(e.startDate)
    } else {
      startDate = DateTime.fromISO(e.startDate)
    }
    const evalStateOffset = startDate.diff(DateTime.fromJSDate(e.meetingDates.start), ['days'])
    const endDate = (evalStateOffset.values.days < 70) ? startDate.plus({days: 13}) : startDate.plus({days: 20})
    if (endDate.diffNow() < 0) {
      evaluationsEnded.push(e)
    }
  })
  if (evaluationsEnded.length) {
    warningMessage = `You're requesting evaluations with an evaluation period that has already ended, which will result in
      those evaluations <strong>NOT being sent to students</strong>. Please set a new start date for the evaluations listed below:<br>`
    each(evaluationsEnded, e => {
      warningMessage += `<br>${e.subjectArea} ${e.catalogId} ${e.instructionFormat} ${e.sectionNumber}`
    })
  }
  return warningMessage
}
