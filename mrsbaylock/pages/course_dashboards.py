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

import itertools
import re
import time

from flask import current_app as app
from mrsbaylock.pages.damien_pages import DamienPages
from mrsbaylock.test_utils import utils
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.wait import WebDriverWait as Wait


class CourseDashboards(DamienPages):
    EVALUATION_ROW = (By.XPATH, '//tr[contains(@class, "evaluation-row")]')
    EVALUATION_STATUS = (By.XPATH, '//td[contains(@id, "-status")]')
    EVALUATION_FORM = (By.XPATH, '//td[contains(@id, "-departmentForm")]')
    EVALUATION_TYPE = (By.XPATH, '//td[contains(@id, "-evaluationType")]')
    EVALUATION_PERIOD = (By.XPATH, '//td[contains(@id, "-period")]')
    NO_SECTIONS_MGS = (By.XPATH, '//span[text()="No eligible sections to load."]')

    @staticmethod
    def eval_row_xpath(evaluation, dept=None, form=None, eval_type=None):
        dept_id = dept.dept_id if dept else evaluation.dept.dept_id
        dept_form = form or evaluation.dept_form
        evaluation_type = eval_type or evaluation.eval_type
        return f'//tr[starts-with(@id, "evaluation-{dept_id}-{evaluation.ccn}-{evaluation.instructor.uid}-{dept_form}-{evaluation_type}")]'

    def rows_of_evaluation(self, evaluation):
        app.logger.info(f'Checking for eval rows at XPath: {self.eval_row_xpath(evaluation)}')
        return self.elements((By.XPATH, self.eval_row_xpath(evaluation)))

    @staticmethod
    def section_row(evaluation):
        return By.XPATH, f'//tr[contains(., "{evaluation.ccn}")]'

    def wait_for_eval_row(self, evaluation, dept=None):
        time.sleep(1)
        self.wait_for_element((By.XPATH, self.eval_row_xpath(evaluation, dept)), utils.get_medium_timeout())

    def visible_evaluation_rows(self):
        return [el.text for el in self.elements(CourseDashboards.EVALUATION_ROW)]

    def visible_evaluation_statuses(self):
        statuses = [el.text.strip() for el in self.elements(CourseDashboards.EVALUATION_STATUS)]
        if 'EDIT' in statuses:
            statuses.remove('EDIT')
        return statuses

    def visible_evaluation_column_selections(self, locator):
        a = []
        for el in self.elements(locator):
            vis_text = el.text.strip()
            if vis_text:
                a.append(vis_text.split()[0])
        return a

    def visible_evaluation_dept_forms(self):
        return self.visible_evaluation_column_selections(CourseDashboards.EVALUATION_FORM)

    def visible_evaluation_types(self):
        return self.visible_evaluation_column_selections(CourseDashboards.EVALUATION_TYPE)

    def visible_evaluation_starts(self):
        return self.visible_evaluation_column_selections(CourseDashboards.EVALUATION_PERIOD)

    def wait_for_eval_rows(self):
        time.sleep(2)
        Wait(self.driver, utils.get_medium_timeout()).until(
            ec.presence_of_all_elements_located(CourseDashboards.EVALUATION_ROW),
        )
        self.hit_tab()
        self.scroll_to_top()
        time.sleep(2)

    def wait_for_no_sections(self):
        time.sleep(1)
        self.wait_for_element(CourseDashboards.NO_SECTIONS_MGS, utils.get_short_timeout())

    @staticmethod
    def expected_eval_data(evals):
        data = []
        for e in evals:
            dates = ''
            if e.eval_start_date:
                dates = f"{e.eval_start_date.strftime('%m/%d/%y')} - {e.eval_end_date.strftime('%m/%d/%y')}"
            if e.instructor is None or e.instructor.uid is None:
                uid = ''
                name = ''
            else:
                uid = e.instructor.uid.strip()
                name = f'{e.instructor.first_name} {e.instructor.last_name}' if e.instructor.first_name else ''
            listings = e.x_listing_ccns or e.room_share_ccns
            if listings:
                listings.sort()
            data.append(
                {
                    'ccn': e.ccn,
                    'listings': (listings or []),
                    'course': f'{e.subject} {e.catalog_id} {e.instruction_format} {e.section_num}',
                    'uid': uid,
                    'name': name,
                    'form': (e.dept_form or ''),
                    'type': (e.eval_type or ''),
                    'dates': dates,
                },
            )
        return data

    def visible_eval_data(self):
        time.sleep(1)
        data = []
        for el in self.elements(CourseDashboards.EVALUATION_STATUS):
            idx = el.get_attribute('id').split('-')[1]
            uid_loc = (By.XPATH, f'//td[@id="evaluation-{idx}-instructor"]/div')
            uid = ''
            name = ''
            if self.is_present(uid_loc):
                parts = self.element(uid_loc).text.strip().split()
                uid = parts[-1].replace('(', '').replace(')', '')
                name = ' '.join(parts[0:-1])
            listings_loc = (By.XPATH, f'//td[@id="evaluation-{idx}-courseNumber"]/div[@class="xlisting-note"]')
            listings = []
            if self.is_present(listings_loc):
                listings = re.sub('[a-zA-Z(,)-]+', '', self.element(listings_loc).text).strip().split()

            data.append(
                {
                    'ccn': self.element((By.ID, f'evaluation-{idx}-courseNumber')).text.strip().split('\n')[0],
                    'listings': listings,
                    'course': self.element((By.ID, f'evaluation-{idx}-courseName')).text.strip(),
                    'uid': uid,
                    'name': name,
                    'form': self.element((By.ID, f'evaluation-{idx}-departmentForm')).text.strip(),
                    'type': self.element((By.ID, f'evaluation-{idx}-evaluationType')).text.strip(),
                    'dates': self.element((By.ID, f'evaluation-{idx}-period')).text.split('\n')[0],
                },
            )
        return data

    def eval_row_el(self, evaluation, dept=None, form=None):
        return self.element((By.XPATH, self.eval_row_xpath(evaluation, dept, form)))

    def eval_status_el(self, evaluation, dept=None, form=None):
        xpath = f'{self.eval_row_xpath(evaluation, dept, form)}/td[contains(@id, "status")]'
        return self.element((By.XPATH, xpath))

    def eval_status(self, evaluation, dept=None, form=None):
        return self.eval_status_el(evaluation, dept, form).text

    def eval_last_update(self, evaluation, dept=None, form=None):
        xpath = f'{self.eval_row_xpath(evaluation, dept, form)}/td[contains(@id, "lastUpdated")]'
        return self.element((By.XPATH, xpath)).text

    def eval_ccn(self, evaluation, dept=None, form=None):
        xpath = f'{self.eval_row_xpath(evaluation, dept, form)}/td[contains(@id, "courseNumber")]'
        return self.element((By.XPATH, xpath)).text.strip().split('\n')[0]

    def eval_course(self, evaluation, dept=None, form=None):
        xpath = f'{self.eval_row_xpath(evaluation, dept, form)}//div[contains(@id, "courseName")]'
        return self.element((By.XPATH, xpath)).text

    def eval_course_title(self, evaluation, dept=None, form=None):
        xpath = f'{self.eval_row_xpath(evaluation, dept, form)}//div[contains(@id, "courseTitle")]'
        return self.element((By.XPATH, xpath)).text

    def eval_instructor(self, evaluation, dept=None, form=None):
        xpath = f'{self.eval_row_xpath(evaluation, dept, form)}/td[contains(@id, "instructor")]'
        return self.element((By.XPATH, xpath)).text

    def eval_dept_form(self, evaluation, dept=None, form=None):
        xpath = f'{self.eval_row_xpath(evaluation, dept, form)}/td[contains(@id, "departmentForm")]'
        return self.element((By.XPATH, xpath)).text.strip()

    def eval_type(self, evaluation, dept=None, form=None):
        xpath = f'{self.eval_row_xpath(evaluation, dept, form)}/td[contains(@id, "evaluationType")]'
        return self.element((By.XPATH, xpath)).text.strip()

    def eval_period_dates(self, evaluation, dept=None, form=None):
        xpath = f'{self.eval_row_xpath(evaluation, dept, form)}/td[contains(@id, "period")]'
        return self.element((By.XPATH, xpath)).text.strip()

    def eval_period_duration(self, evaluation, dept=None, form=None):
        xpath = f'{self.eval_row_xpath(evaluation, dept, form)}/td[contains(@id, "period")]/span/div[2]'
        return self.element((By.XPATH, xpath)).text.strip()

    # FILTERING

    SEARCH_INPUT = (By.ID, 'evaluation-search-input')

    def filter_rows(self, search_string):
        app.logger.info(f'Filtering table by {search_string}')
        self.remove_and_enter_chars(CourseDashboards.SEARCH_INPUT, search_string)
        time.sleep(utils.get_short_timeout())

    # SORTING

    def sort_asc(self, header_string):
        self.wait_for_element((By.XPATH, f'//th[contains(., "{header_string}")]'), utils.get_short_timeout())
        sort = self.element((By.XPATH, f'//th[contains(., "{header_string}")]')).get_attribute('aria-sort')
        if sort == 'none' or sort == 'descending':
            el = self.element((By.XPATH, f'//th[contains(., "{header_string}")]/button'))
            el.click()
            if sort == 'descending':
                time.sleep(utils.get_click_sleep())
                el.click()
        time.sleep(2)

    def sort_desc(self, header_string):
        self.wait_for_element((By.XPATH, f'//th[contains(., "{header_string}")]'), utils.get_short_timeout())
        sort = self.element((By.XPATH, f'//th[contains(., "{header_string}")]')).get_attribute('aria-sort')
        if sort == 'none' or sort == 'ascending':
            el = self.element((By.XPATH, f'//th[contains(., "{header_string}")]/button'))
            el.click()
            if sort == 'none':
                time.sleep(utils.get_click_sleep())
                el.click()
        time.sleep(2)

    @staticmethod
    def sort_default(evaluations, reverse=False):
        evaluations.sort(
            key=lambda e: (
                e.subject,
                int(''.join([i for i in e.catalog_id if i.isdigit()])),
                (e.catalog_id.split(''.join([i for i in e.catalog_id if i.isdigit()]))[1]),
                e.instruction_format,
                e.section_num,
                (e.eval_type or ''),
                (e.dept_form or ''),
                (e.instructor.last_name.lower() if e.instructor.uid else ''),
                (e.instructor.first_name.lower() if e.instructor.uid else ''),
                e.eval_start_date,
            ),
            reverse=reverse,
        )

    @staticmethod
    def split_listings(dept, evaluations, exempt_status=False):
        dept_subj = utils.get_dept_subject_areas(dept)
        domestic_listings = list(filter(lambda e: e.subject in dept_subj, evaluations))
        foreign_listings = [e for e in evaluations if e not in domestic_listings]
        # Treat domestic room shares like foreigners
        for listing in domestic_listings:
            ccns = listing.room_share_ccns
            matches = [ev for ev in domestic_listings if ev.ccn in ccns and ev.ccn != listing.ccn]
            for match in matches:
                foreign_listings.append(match)
                domestic_listings.remove(match)

        if exempt_status:
            for listing in domestic_listings:
                ccns = listing.x_listing_ccns
                matches = [ev for ev in foreign_listings if ev.ccn in ccns and ev.ccn != listing.ccn]
                for match in matches:
                    if listing.status != match.status:
                        foreign_listings.remove(match)
                        domestic_listings.append(match)

        foreign_listings.sort(
            key=lambda e: (
                e.subject,
                (e.instructor.last_name.lower() if e.instructor.uid else ''),
                (e.instructor.first_name.lower() if e.instructor.uid else ''),
            ),
        )
        return domestic_listings, foreign_listings

    @staticmethod
    def pair_foreign_listings(domestic_grp, foreign_listings):
        foreign_grp = []
        ccns = domestic_grp[0].x_listing_ccns or domestic_grp[0].room_share_ccns
        for foreigner in foreign_listings:
            for ccn in ccns:
                matches = []
                for ev in domestic_grp:
                    if foreigner.ccn == ccn and (
                            foreigner.instructor.uid == ev.instructor.uid) and foreigner not in matches:
                        matches.append(foreigner)
                if matches:
                    foreign_grp.append(matches)
        foreign_grp.sort(
            key=lambda f: (
                (f[0].instructor.last_name.lower() if f[0].instructor.last_name else ''),
                (f[0].instructor.first_name.lower() if f[0].instructor.first_name else ''),
            ),
        )
        return foreign_grp

    @staticmethod
    def insert_x_listings_and_shares(domestic_listings, foreign_listings, reverse, reverse_instructors=False):
        evaluations = []
        grouped_evals = itertools.groupby(domestic_listings, key=lambda c: c.ccn)
        for k, g in grouped_evals:
            domestic_grp = list(g)
            domestic_grp.sort(
                key=lambda d: (
                    (d.instructor.last_name.lower() if d.instructor.last_name else ''),
                    (d.instructor.first_name.lower() if d.instructor.first_name else ''),
                ),
                reverse=reverse_instructors,
            )
            foreign_grp = CourseDashboards.pair_foreign_listings(domestic_grp, foreign_listings)
            all_grp = [i for i in foreign_grp]
            if reverse:
                all_grp.append(domestic_grp)
            else:
                all_grp.insert(0, domestic_grp)
            all_grp = itertools.chain(*all_grp)
            for listing in all_grp:
                evaluations.append(listing)
        return evaluations

    @staticmethod
    def get_catalog_id_suffix(evaluation):
        num = ''.join([i for i in evaluation.catalog_id if i.isdigit()])
        return evaluation.catalog_id.split(num)[1]

    def sort_by_course(self, dept, evaluations, reverse=False):
        domestic_listings, foreign_listings = self.split_listings(dept, evaluations)
        for listings in [domestic_listings, foreign_listings]:
            self.sort_default(listings, reverse)
        return self.insert_x_listings_and_shares(domestic_listings, foreign_listings, reverse)

    def sort_by_status(self, dept, evaluations, reverse=False):
        domestic_listings, foreign_listings = self.split_listings(dept, evaluations, exempt_status=True)
        for listings in [domestic_listings, foreign_listings]:
            self.sort_default(listings, reverse=False)
        domestic_listings.sort(key=lambda e: (e.status.value['ui'] if e.status else ''), reverse=reverse)
        return self.insert_x_listings_and_shares(domestic_listings, foreign_listings, reverse=False)

    def sort_by_ccn(self, dept, evaluations, reverse=False):
        domestic_listings, foreign_listings = self.split_listings(dept, evaluations)
        foreign_listings.sort(key=lambda e: int(e.ccn), reverse=reverse)
        domestic_listings.sort(
            key=lambda e: (
                int(e.ccn),
                (e.eval_type or ''),
                (e.dept_form or ''),
                (e.instructor.last_name.lower() if e.instructor.uid else ''),
                (e.instructor.first_name.lower() if e.instructor.uid else ''),
                e.eval_start_date,
            ),
            reverse=reverse,
        )
        return self.insert_x_listings_and_shares(domestic_listings, foreign_listings, reverse)

    def sort_by_instructor(self, dept, evaluations, reverse=False):
        domestic_listings, foreign_listings = self.split_listings(dept, evaluations)
        for listings in [domestic_listings, foreign_listings]:
            self.sort_default(listings, reverse=False)
        domestic_listings.sort(
            key=lambda e: (
                (e.instructor.last_name.lower() if e.instructor.uid else ''),
                (e.instructor.first_name.lower() if e.instructor.uid else ''),
                e.instructor.uid,
                (e.eval_type or ''),
                (e.dept_form or ''),
                e.eval_start_date,
            ),
            reverse=reverse,
        )
        sorted_lists = []
        grouped = itertools.groupby(domestic_listings, key=lambda d: d.instructor.uid)
        for k, g in grouped:
            sections = list(g)
            sections.sort(
                key=lambda l: (
                    l.subject,
                    int(''.join([x for x in l.catalog_id if x.isdigit()])),
                    (l.catalog_id.split(''.join([x for x in l.catalog_id if x.isdigit()]))[1]),
                    l.instruction_format,
                    l.section_num,
                ),
            )
            for i in sections:
                sorted_lists.append(i)
        return self.insert_x_listings_and_shares(sorted_lists, foreign_listings, reverse=False,
                                                 reverse_instructors=reverse)

    def sort_by_dept_form(self, dept, evaluations, reverse=False):
        domestic_listings, foreign_listings = self.split_listings(dept, evaluations)
        for listings in [domestic_listings, foreign_listings]:
            self.sort_default(listings, reverse=False)
        domestic_listings.sort(key=lambda e: (e.dept_form or ''), reverse=reverse)
        return self.insert_x_listings_and_shares(domestic_listings, foreign_listings, reverse=False)

    def sort_by_eval_type(self, dept, evaluations, reverse=False):
        domestic_listings, foreign_listings = self.split_listings(dept, evaluations)
        for listings in [domestic_listings, foreign_listings]:
            self.sort_default(listings, reverse=False)
        domestic_listings.sort(
            key=lambda e: (e.eval_type or ''), reverse=reverse)
        return self.insert_x_listings_and_shares(domestic_listings, foreign_listings, reverse=False)

    def sort_by_eval_period(self, dept, evaluations, reverse=False):
        domestic_listings, foreign_listings = self.split_listings(dept, evaluations)
        for listings in [domestic_listings, foreign_listings]:
            self.sort_default(listings, reverse=False)
        all_listings = self.insert_x_listings_and_shares(domestic_listings, foreign_listings, reverse=False)
        all_listings.sort(key=lambda e: e.eval_start_date, reverse=reverse)
        return all_listings

    @staticmethod
    def sorted_eval_data(evaluations):
        data = []
        for e in evaluations:
            data.append(
                {
                    'ccn': e.ccn,
                    'course': f'{e.subject} {e.catalog_id} {e.instruction_format} {e.section_num}',
                    'uid': (e.instructor.uid or ''),
                },
            )
        return data

    def visible_sorted_eval_data(self):
        data = self.visible_eval_data()
        for d in data:
            d.pop('dates')
            d.pop('name')
            d.pop('form')
            d.pop('type')
            d.pop('listings')
        return data
