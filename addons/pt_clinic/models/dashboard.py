import base64
from datetime import datetime, time

import pytz

from odoo import fields, models, tools


class PtClinicDashboard(models.Model):
    _name = "pt.clinic.dashboard"
    _description = "Wiqaya Clinic Dashboard"

    name = fields.Char(default="Wiqaya", required=True, translate=True)

    def init(self):
        super().init()
        self.env.cr.execute(
            """
            SELECT udt_name
              FROM information_schema.columns
             WHERE table_name = 'pt_clinic_dashboard'
               AND column_name = 'name'
            """
        )
        column_info = self.env.cr.fetchone()
        if column_info and column_info[0] != "jsonb":
            self.env.cr.execute(
                """
                ALTER TABLE pt_clinic_dashboard
                ALTER COLUMN name TYPE jsonb
                USING CASE
                    WHEN name IS NULL THEN NULL
                    ELSE jsonb_build_object('en_US', name::text)
                END
                """
            )

    patient_count = fields.Integer(compute="_compute_counts")
    appointment_today_count = fields.Integer(compute="_compute_counts")
    assessment_count = fields.Integer(compute="_compute_counts")
    active_plan_count = fields.Integer(compute="_compute_counts")
    session_count = fields.Integer(compute="_compute_counts")
    package_count = fields.Integer(compute="_compute_counts")
    reminder_pending_count = fields.Integer(compute="_compute_counts")

    def _today_utc_bounds(self):
        """Return the current user's local day as UTC-naive datetimes for Odoo domains."""
        today = fields.Date.context_today(self)
        user_tz = pytz.timezone(self.env.user.tz or "UTC")
        start_local = user_tz.localize(datetime.combine(today, time.min))
        end_local = user_tz.localize(datetime.combine(today, time.max))
        return (
            start_local.astimezone(pytz.UTC).replace(tzinfo=None),
            end_local.astimezone(pytz.UTC).replace(tzinfo=None),
        )

    def _company_count(self, model_name, extra_domain=None):
        domain = [("clinic_company_id", "=", self.env.company.id)]
        if extra_domain:
            domain.extend(extra_domain)
        return self.env[model_name].search_count(domain)

    def _compute_counts(self):
        start_day, end_day = self._today_utc_bounds()
        counts = {
            "patient_count": self._company_count("pt.patient"),
            "appointment_today_count": self._company_count(
                "pt.appointment",
                [
                    ("start_datetime", ">=", start_day),
                    ("start_datetime", "<=", end_day),
                    ("status", "in", ["draft", "confirmed"]),
                ],
            ),
            "assessment_count": self._company_count("pt.assessment"),
            "active_plan_count": self._company_count("pt.treatment.plan", [("status", "=", "active")]),
            "session_count": self._company_count("pt.session"),
            "package_count": self._company_count("pt.treatment.package"),
            "reminder_pending_count": self._company_count(
                "pt.appointment", [("status", "in", ["draft", "confirmed"]), ("reminder_sent", "=", False)]
            ),
        }
        for record in self:
            for field_name, value in counts.items():
                record[field_name] = value

    def _action_from_xmlid(self, xmlid):
        return self.env.ref(xmlid).sudo().read()[0]

    def _get_preferred_arabic_lang(self):
        installed_codes = set(self.env["res.lang"].search([]).mapped("code"))
        for code in ("ar_001", "ar_EG", "ar"):
            if code in installed_codes:
                return code
        return False

    def action_open_patients(self):
        return self._action_from_xmlid("pt_clinic.action_pt_patient")

    def action_open_appointments(self):
        return self._action_from_xmlid("pt_clinic.action_pt_appointment")

    def action_open_assessments(self):
        return self._action_from_xmlid("pt_clinic.action_pt_assessment")

    def action_open_treatment_plans(self):
        return self._action_from_xmlid("pt_clinic.action_pt_treatment_plan")

    def action_open_sessions(self):
        return self._action_from_xmlid("pt_clinic.action_pt_session")

    def action_open_packages(self):
        return self._action_from_xmlid("pt_clinic.action_pt_package")

    def action_open_billing(self):
        return self._action_from_xmlid("pt_clinic.action_pt_session_invoicing_wizard")

    def action_open_reports(self):
        return self._action_from_xmlid("pt_clinic.action_pt_session_reporting")

    def action_open_settings(self):
        return self._action_from_xmlid("pt_clinic.action_pt_branch")

    def apply_wiqaya_branding(self):
        arabic_lang = self._get_preferred_arabic_lang()

        with tools.file_open("pt_clinic/static/src/img/wiqaya_logo.png", "rb") as logo_file:
            logo_b64 = base64.b64encode(logo_file.read())

        company = self.env.ref("base.main_company", raise_if_not_found=False)
        if company:
            company.write({"name": "Wiqaya", "logo": logo_b64})

        for xmlid in ("base.user_admin", "base.default_user"):
            user = self.env.ref(xmlid, raise_if_not_found=False)
            if user and user.partner_id and arabic_lang:
                user.partner_id.lang = arabic_lang

        main_branches = self.env["pt.branch"].search([("code", "=", "MAIN")])
        if main_branches:
            main_branches.write({"name": "Wiqaya - Main Branch", "active": True})
            if arabic_lang:
                main_branches.with_context(lang=arabic_lang).write({"name": "وقاية - الفرع الرئيسي"})

        legacy_branches = self.env["pt.branch"].search([("name", "ilike", "Damietta")])
        if legacy_branches:
            legacy_branches.write({"active": False})

        root_menu = self.env.ref("pt_clinic.menu_pt_clinic_root", raise_if_not_found=False)
        if root_menu:
            root_menu.write({"name": "Wiqaya", "web_icon": "pt_clinic,static/src/img/wiqaya_logo.png"})
            if arabic_lang:
                root_menu.with_context(lang=arabic_lang).write({"name": "وقاية"})

        dashboard_action = self.env.ref("pt_clinic.action_pt_clinic_dashboard", raise_if_not_found=False)
        if dashboard_action:
            dashboard_action.write({"name": "Wiqaya"})
            if arabic_lang:
                dashboard_action.with_context(lang=arabic_lang).write({"name": "وقاية"})
        return True
