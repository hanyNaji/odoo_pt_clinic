import base64

from odoo import fields, models, tools


class PtClinicDashboard(models.Model):
    _name = "pt.clinic.dashboard"
    _description = "Wiqaya Clinic Dashboard"

    name = fields.Char(default="وقاية", required=True)
    patient_count = fields.Integer(compute="_compute_counts")
    appointment_today_count = fields.Integer(compute="_compute_counts")
    assessment_count = fields.Integer(compute="_compute_counts")
    active_plan_count = fields.Integer(compute="_compute_counts")
    session_count = fields.Integer(compute="_compute_counts")
    package_count = fields.Integer(compute="_compute_counts")
    reminder_pending_count = fields.Integer(compute="_compute_counts")

    def _compute_counts(self):
        today = fields.Date.context_today(self)
        start_day = fields.Datetime.to_datetime(f"{today} 00:00:00")
        end_day = fields.Datetime.to_datetime(f"{today} 23:59:59")
        company_id = self.env.company.id
        for record in self:
            record.patient_count = self.env["pt.patient"].search_count([("clinic_company_id", "=", company_id)])
            record.appointment_today_count = self.env["pt.appointment"].search_count(
                [
                    ("clinic_company_id", "=", company_id),
                    ("start_datetime", ">=", start_day),
                    ("start_datetime", "<=", end_day),
                    ("status", "in", ["draft", "confirmed"]),
                ]
            )
            record.assessment_count = self.env["pt.assessment"].search_count([("clinic_company_id", "=", company_id)])
            record.active_plan_count = self.env["pt.treatment.plan"].search_count(
                [("clinic_company_id", "=", company_id), ("status", "=", "active")]
            )
            record.session_count = self.env["pt.session"].search_count([("clinic_company_id", "=", company_id)])
            record.package_count = self.env["pt.treatment.package"].search_count([("clinic_company_id", "=", company_id)])
            record.reminder_pending_count = self.env["pt.appointment"].search_count(
                [
                    ("clinic_company_id", "=", company_id),
                    ("status", "in", ["draft", "confirmed"]),
                    ("reminder_sent", "=", False),
                ]
            )

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
            company.write({"name": "وقاية", "logo": logo_b64})

        for xmlid in ("base.user_admin", "base.default_user"):
            user = self.env.ref(xmlid, raise_if_not_found=False)
            if user and user.partner_id and arabic_lang:
                user.partner_id.lang = arabic_lang

        main_branches = self.env["pt.branch"].search([("code", "=", "MAIN")])
        if main_branches:
            main_branches.write({"name": "وقاية - الفرع الرئيسي", "active": True})

        legacy_branches = self.env["pt.branch"].search([("name", "ilike", "Damietta")])
        if legacy_branches:
            legacy_branches.write({"active": False})

        root_menu = self.env.ref("pt_clinic.menu_pt_clinic_root", raise_if_not_found=False)
        if root_menu:
            root_menu.write({"name": "وقاية", "web_icon": "pt_clinic,static/src/img/wiqaya_logo.png"})
            if arabic_lang:
                root_menu.with_context(lang=arabic_lang).write({"name": "وقاية"})

        dashboard_action = self.env.ref("pt_clinic.action_pt_clinic_dashboard", raise_if_not_found=False)
        if dashboard_action:
            dashboard_action.write({"name": "وقاية"})
            if arabic_lang:
                dashboard_action.with_context(lang=arabic_lang).write({"name": "وقاية"})
        return True
