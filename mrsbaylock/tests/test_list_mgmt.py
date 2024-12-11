"""
Copyright ©2023. The Regents of the University of California (Regents). All Rights Reserved.

Permission to use, copy, modify, and distribute this software and its documentation
for educational, research, and not-for-profit purposes, without fee and without a
signed licensing agreement, is hereby granted, provided that the above copyright
notice, this paragraph and the following two paragraphs appear in all copies,
modifications, and distributions.

Contact The Office of Technology Licensing, UC Berkeley, 2150 Shattuck Avenue,
Suite 510, Berkeley, CA 94720-1620, (510) 643-7201, otl@berkeley.edu,
http://ipira.berkeley.edu/industry-info for commercial licensing opportunities.

IN NO EVENT SHALL REGENTS BE LIABLE TO ANY PARTY FOR DIRECT, INDIRECT, SPECIAL,
INCIDENTAL, OR CONSEQUENTIAL DAMAGES, INCLUDING LOST PROFITS, ARISING OUT OF
THE USE OF THIS SOFTWARE AND ITS DOCUMENTATION, EVEN IF REGENTS HAS BEEN ADVISED
OF THE POSSIBILITY OF SUCH DAMAGE.

REGENTS SPECIFICALLY DISCLAIMS ANY WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE. THE
SOFTWARE AND ACCOMPANYING DOCUMENTATION, IF ANY, PROVIDED HEREUNDER IS PROVIDED
"AS IS". REGENTS HAS NO OBLIGATION TO PROVIDE MAINTENANCE, SUPPORT, UPDATES,
ENHANCEMENTS, OR MODIFICATIONS.
"""

import time

from mrsbaylock.models.evaluation_status import EvaluationStatus
from mrsbaylock.pages.course_dashboard_edits_page import CourseDashboardEditsPage
from mrsbaylock.test_utils import evaluation_utils
from mrsbaylock.test_utils import utils
import pytest


@pytest.mark.usefixtures('page_objects')
class TestListManagement:

    test_id = f'{int(time.mktime(time.gmtime()))}'
    term = utils.get_current_term()
    utils.reset_test_data(term)
    all_contacts = utils.get_all_users()
    dept = utils.get_test_dept_1()
    dept.evaluations = evaluation_utils.get_evaluations(term, dept, log=True)
    evaluations = list(filter(lambda e: e.instructor.uid, dept.evaluations))
    eval_unmarked = evaluations[0]
    eval_to_review = evaluations[1]
    eval_confirmed = evaluations[2]
    eval_duped = evaluations[3]
    confirmed = []
    form = f'Form_{test_id}'
    eval_type = f'Type_{test_id}'
    alert = (f'FOO {test_id} ' * 15).strip()

    instructor = utils.get_test_user()
    instructor.first_name = instructor.first_name[::-1]
    instructor.last_name = instructor.last_name[::-1]

    def test_clear_cache(self):
        self.login_page.load_page()
        self.login_page.dev_auth()
        self.status_board_admin_page.click_list_mgmt()
        self.api_page.refresh_unholy_loch()

    def test_list_mgmt_page(self):
        self.homepage.load_page()
        self.status_board_admin_page.click_list_mgmt()

    # ADDING FORM, TYPE, AND INSTRUCTOR

    def test_add_dept_form(self):
        self.list_mgmt_page.add_dept_form(self.form)
        assert self.form in self.list_mgmt_page.visible_dept_form_names()

    def test_add_eval_type(self):
        self.list_mgmt_page.add_eval_type(self.eval_type)
        assert self.eval_type in self.list_mgmt_page.visible_eval_type_names()

    def test_add_instructor(self):
        self.list_mgmt_page.add_manual_instructor(self.instructor)
        self.list_mgmt_page.wait_for_manual_instructor(self.instructor)

    def test_unmarked_add_form_and_type(self):
        self.dept_details_admin_page.load_dept_page(self.dept)
        self.dept_details_admin_page.click_edit_evaluation(self.eval_unmarked)
        self.dept_details_admin_page.select_eval_status(self.eval_unmarked, EvaluationStatus.UNMARKED)
        self.dept_details_admin_page.change_dept_form(self.eval_unmarked, self.form)
        self.dept_details_admin_page.change_eval_type(self.eval_unmarked, self.eval_type)
        self.dept_details_admin_page.save_eval_changes(self.eval_unmarked)
        self.eval_unmarked.dept_form = self.form
        self.eval_unmarked.eval_type = self.eval_type
        self.dept_details_admin_page.wait_for_eval_rows()
        assert EvaluationStatus.UNMARKED.value['ui'] in self.dept_details_admin_page.eval_status(self.eval_unmarked)
        assert self.form in self.dept_details_admin_page.eval_dept_form(self.eval_unmarked)
        assert self.eval_type in self.dept_details_admin_page.eval_type(self.eval_unmarked)

    def test_for_review_add_form_and_type(self):
        self.dept_details_admin_page.click_edit_evaluation(self.eval_to_review)
        self.dept_details_admin_page.select_eval_status(self.eval_to_review, EvaluationStatus.FOR_REVIEW)
        self.dept_details_admin_page.change_dept_form(self.eval_to_review, self.form)
        self.dept_details_admin_page.change_eval_type(self.eval_to_review, self.eval_type)
        self.dept_details_admin_page.save_eval_changes(self.eval_to_review)
        self.eval_to_review.dept_form = self.form
        self.eval_to_review.eval_type = self.eval_type
        self.eval_to_review.status = EvaluationStatus.FOR_REVIEW
        self.dept_details_admin_page.wait_for_eval_rows()
        assert EvaluationStatus.FOR_REVIEW.value['ui'] in self.dept_details_admin_page.eval_status(self.eval_to_review)
        assert self.form in self.dept_details_admin_page.eval_dept_form(self.eval_to_review)
        assert self.eval_type in self.dept_details_admin_page.eval_type(self.eval_to_review)

    def test_confirmed_add_form_and_type(self):
        self.dept_details_admin_page.click_edit_evaluation(self.eval_confirmed)
        self.dept_details_admin_page.select_eval_status(self.eval_confirmed, EvaluationStatus.CONFIRMED)
        self.dept_details_admin_page.change_dept_form(self.eval_confirmed, self.form)
        self.dept_details_admin_page.change_eval_type(self.eval_confirmed, self.eval_type)
        self.dept_details_admin_page.save_eval_changes(self.eval_confirmed, EvaluationStatus.CONFIRMED)
        self.eval_confirmed.dept_form = self.form
        self.eval_confirmed.eval_type = self.eval_type
        self.eval_confirmed.status = EvaluationStatus.CONFIRMED
        self.dept_details_admin_page.wait_for_eval_rows()
        assert EvaluationStatus.CONFIRMED.value['ui'] in self.dept_details_admin_page.eval_status(self.eval_confirmed)
        assert self.form in self.dept_details_admin_page.eval_dept_form(self.eval_confirmed)
        assert self.eval_type in self.dept_details_admin_page.eval_type(self.eval_confirmed)

    def test_confirmed_dupe_instructor(self):
        self.dept_details_admin_page.click_eval_checkbox(self.eval_duped)
        self.dept_details_admin_page.duplicate_section(self.eval_duped, self.evaluations,
                                                       instructor=self.instructor, eval_type=self.eval_type)
        dupe = self.evaluations[-1]
        self.dept_details_admin_page.click_edit_evaluation(dupe)
        self.dept_details_admin_page.select_eval_status(self.eval_confirmed, EvaluationStatus.CONFIRMED)
        self.dept_details_admin_page.change_dept_form(self.eval_confirmed, self.form)
        self.dept_details_admin_page.save_eval_changes(self.eval_confirmed, EvaluationStatus.CONFIRMED)
        dupe.dept_form = self.form
        dupe.status = EvaluationStatus.CONFIRMED
        self.dept_details_admin_page.wait_for_eval_rows()
        assert self.instructor.uid in self.dept_details_admin_page.eval_instructor(dupe)
        assert self.instructor.first_name in self.dept_details_admin_page.eval_instructor(dupe)
        assert self.instructor.last_name in self.dept_details_admin_page.eval_instructor(dupe)

    # DELETING FORM, TYPE, AND INSTRUCTOR

    def test_delete_dept_form(self):
        self.dept_details_admin_page.click_list_mgmt()
        self.list_mgmt_page.delete_dept_form(self.form)
        assert self.form not in self.list_mgmt_page.visible_dept_form_names()

    def test_delete_eval_type(self):
        self.list_mgmt_page.delete_eval_type(self.eval_type)
        assert self.eval_type not in self.list_mgmt_page.visible_eval_type_names()

    def test_unmarked_form_and_type_deleted(self):
        self.eval_unmarked.dept_form = self.eval_unmarked.default_dept_form
        self.dept_details_admin_page.load_dept_page(self.dept)
        assert self.form not in self.dept_details_admin_page.eval_dept_form(self.eval_unmarked)
        assert self.dept_details_admin_page.eval_type(self.eval_unmarked) == self.eval_type

    def test_for_review_form_and_type_deleted(self):
        self.eval_to_review.dept_form = self.eval_to_review.default_dept_form
        assert self.form not in self.dept_details_admin_page.eval_dept_form(self.eval_to_review)
        assert self.dept_details_admin_page.eval_type(self.eval_to_review) == self.eval_type

    def test_confirmed_form_and_type_deleted(self):
        assert self.dept_details_admin_page.eval_dept_form(self.eval_confirmed) == self.form
        assert self.dept_details_admin_page.eval_type(self.eval_confirmed) == self.eval_type

    def test_deleted_form_not_available(self):
        self.dept_details_admin_page.click_edit_evaluation(self.eval_unmarked)
        self.dept_details_admin_page.click_dept_form_input()
        assert self.form not in self.dept_details_admin_page.visible_dept_form_options()

    def test_deleted_type_not_available(self):
        assert self.eval_type not in self.dept_details_admin_page.visible_eval_type_options()

    def test_deleted_form_available_on_dept_contact(self):
        self.dept_details_admin_page.click_cancel_eval_changes()
        self.dept_details_admin_page.reload_page()
        self.dept_details_admin_page.click_add_contact()
        self.dept_details_admin_page.look_up_uid(self.instructor.uid, CourseDashboardEditsPage.ADD_CONTACT_LOOKUP_INPUT)
        self.dept_details_admin_page.click_look_up_result(self.instructor)
        self.dept_details_admin_page.clear_dept_form_input()
        self.dept_details_admin_page.enter_and_select_dept_form(self.form)

    def test_delete_manual_instructor(self):
        self.dept_details_admin_page.click_list_mgmt()
        self.list_mgmt_page.delete_manual_instructor(self.instructor)

    def test_deleted_instructor_not_available(self):
        self.dept_details_admin_page.load_dept_page(self.dept)
        self.dept_details_admin_page.click_eval_checkbox(self.dept.evaluations[0])
        self.dept_details_admin_page.wait_for_element_and_click(CourseDashboardEditsPage.DUPE_BUTTON)
        self.dept_details_admin_page.look_up_uid(self.instructor.uid, CourseDashboardEditsPage.DUPE_SECTION_INSTR_INPUT)
        self.dept_details_admin_page.wait_for_element(
            self.dept_details_admin_page.add_contact_lookup_result(self.instructor),
            utils.get_short_timeout())
        result_text = self.dept_details_admin_page.element(self.dept_details_admin_page.add_contact_lookup_result(self.instructor)).text
        assert self.instructor.first_name not in result_text
        assert self.instructor.last_name not in result_text

    # PUBLISH WITH DELETED FORM, TYPE, AND INSTRUCTOR

    def test_publish(self):
        evals = evaluation_utils.get_evaluations(self.term, self.dept)
        confirmed = list(filter(lambda ev: (ev.status == EvaluationStatus.CONFIRMED), evals))
        self.confirmed.extend(confirmed)
        self.publish_page.load_page()
        self.publish_page.download_export_csvs()

    def test_get_course_ids(self):
        utils.calculate_course_ids(self.confirmed)

    def test_courses(self):
        expected = utils.expected_courses(self.confirmed)
        actual = self.publish_page.parse_csv('courses')
        utils.verify_actual_matches_expected(actual, expected)

    def test_course_instructors(self):
        expected = utils.expected_course_instructors(self.confirmed)
        actual = self.publish_page.parse_csv('course_instructors')
        current_term_rows = list(filter(lambda r: (self.term.prefix in r['COURSE_ID']), actual))
        utils.verify_actual_matches_expected(current_term_rows, expected)

    def test_course_supervisors(self):
        expected = utils.expected_course_supervisors(self.confirmed, self.all_contacts)
        actual = self.publish_page.parse_csv('course_supervisors')
        utils.verify_actual_matches_expected(actual, expected)

    def test_dept_hierarchy(self):
        expected_dept_hierarchy = utils.expected_dept_hierarchy()
        csv_dept_hierarchy = self.publish_page.parse_csv('department_hierarchy')
        utils.verify_actual_matches_expected(csv_dept_hierarchy, expected_dept_hierarchy)

    def test_report_viewers(self):
        expected_viewers = utils.expected_report_viewers()
        csv_viewers = self.publish_page.parse_csv('report_viewer_hierarchy')
        utils.verify_actual_matches_expected(csv_viewers, expected_viewers)

    # SERVICE ALERTS

    def test_save_unposted_alert(self):
        self.status_board_admin_page.load_page()
        self.status_board_admin_page.click_list_mgmt()
        self.list_mgmt_page.enter_service_alert(self.alert)
        if self.list_mgmt_page.is_service_alert_posted():
            self.list_mgmt_page.click_publish_alert_cbx()
        self.list_mgmt_page.save_service_alert()
        assert not self.list_mgmt_page.service_alert()

    def test_post_alert(self):
        self.list_mgmt_page.click_publish_alert_cbx()
        self.list_mgmt_page.save_service_alert()
        assert self.list_mgmt_page.service_alert() == self.alert

    def test_edit_posted_alert(self):
        self.list_mgmt_page.enter_service_alert(f'EDITED {self.alert}')
        self.list_mgmt_page.save_service_alert()
        assert self.list_mgmt_page.service_alert() == f'EDITED {self.alert}'

    def test_unpost_alert(self):
        self.list_mgmt_page.click_publish_alert_cbx()
        self.list_mgmt_page.save_service_alert()
        assert not self.list_mgmt_page.service_alert()
