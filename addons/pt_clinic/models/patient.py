import re

from odoo import api, fields, models
from odoo.exceptions import ValidationError


class PtPatient(models.Model):
    _name = "pt.patient"
    _description = "Wiqaya Patient"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _rec_names_search = ["name", "code", "phone", "whatsapp", "national_id"]
    _code_uniq = models.Constraint(
        "unique(code)",
        "Patient code must be unique.",
    )
    _national_id_uniq = models.Constraint(
        "unique(national_id)",
        "National ID must be unique.",
    )

    @api.model
    def _default_branch_id(self):
        branch = self.env["pt.branch"].search(
            [("clinic_company_id", "=", self.env.company.id), ("active", "=", True)],
            limit=1,
        )
        return branch.id

    name = fields.Char(string="Patient Name", required=True, tracking=True)
    code = fields.Char(string="File Code", default="New", readonly=True, copy=False, index=True)
    partner_id = fields.Many2one("res.partner", string="Contact", required=True, ondelete="restrict")
    clinic_company_id = fields.Many2one(
        "res.company", string="Company", required=True, default=lambda self: self.env.company, index=True
    )
    branch_id = fields.Many2one(
        "pt.branch",
        string="Branch",
        domain="[('clinic_company_id', '=', clinic_company_id)]",
        default=_default_branch_id,
        tracking=True,
        index=True,
    )
    birth_date = fields.Date(string="Date of Birth")
    age_years = fields.Integer(string="Age", compute="_compute_age_years", store=False)
    gender = fields.Selection(
        [("male", "Male"), ("female", "Female"), ("other", "Other")],
        string="Gender",
        default="other",
    )
    national_id = fields.Char(string="National ID", tracking=True, index=True)
    governorate = fields.Selection(
        [
            ("damietta", "Damietta"),
            ("dakahlia", "Dakahlia"),
            ("cairo", "Cairo"),
            ("alexandria", "Alexandria"),
            ("other", "Other"),
        ],
        string="Governorate",
        default="damietta",
    )
    phone = fields.Char(string="Phone", related="partner_id.phone", store=True, readonly=False, index=True)
    email = fields.Char(string="Email", related="partner_id.email", store=True, readonly=False, index=True)
    whatsapp = fields.Char(string="WhatsApp", index=True)
    job_title = fields.Char(string="Job")
    primary_physician = fields.Char(string="Primary Physician")
    emergency_contact = fields.Char(string="Emergency Contact")
    emergency_relation = fields.Char(string="Relation")
    medical_history = fields.Text(string="Medical History")
    allergy_notes = fields.Text(string="Allergy Notes")
    company_id = fields.Many2one(
        "res.partner", string="Employer Company", domain=[("is_company", "=", True)]
    )
    active = fields.Boolean(string="Active", default=True, index=True)
    appointment_ids = fields.One2many("pt.appointment", "patient_id", string="Appointments")
    session_ids = fields.One2many("pt.session", "patient_id", string="Sessions")
    assessment_ids = fields.One2many("pt.assessment", "patient_id", string="Assessments")
    treatment_plan_ids = fields.One2many("pt.treatment.plan", "patient_id", string="Care Plans")
    therapy_sheet_ids = fields.One2many("pt.therapy.sheet", "patient_id", string="Therapy Sheets")

    @api.depends("birth_date")
    def _compute_age_years(self):
        today = fields.Date.context_today(self)
        for record in self:
            if not record.birth_date:
                record.age_years = 0
                continue
            age = today.year - record.birth_date.year
            if (today.month, today.day) < (record.birth_date.month, record.birth_date.day):
                age -= 1
            record.age_years = max(age, 0)

    @api.constrains("national_id")
    def _check_national_id(self):
        for record in self:
            if record.national_id and not re.fullmatch(r"\d{14}", record.national_id):
                raise ValidationError("National ID must be exactly 14 digits.")

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("code", "New") == "New":
                vals["code"] = self.env["ir.sequence"].next_by_code("pt.patient") or "New"
            vals.setdefault("clinic_company_id", self.env.company.id)
            if not vals.get("branch_id"):
                branch = self.env["pt.branch"].search(
                    [("clinic_company_id", "=", vals["clinic_company_id"]), ("active", "=", True)],
                    limit=1,
                )
                vals["branch_id"] = branch.id
        return super().create(vals_list)
