import re

from odoo import api, fields, models
from odoo.exceptions import ValidationError


class PtPatient(models.Model):
    _name = "pt.patient"
    _description = "Wiqaya Patient"
    _inherit = ["mail.thread", "mail.activity.mixin"]
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

    name = fields.Char(string="اسم المريض | Patient Name", required=True, tracking=True)
    code = fields.Char(string="كود الملف | File Code", default="New", readonly=True, copy=False)
    partner_id = fields.Many2one("res.partner", string="جهة الاتصال | Contact", required=True, ondelete="restrict")
    clinic_company_id = fields.Many2one(
        "res.company", string="الشركة | Company", required=True, default=lambda self: self.env.company, index=True
    )
    branch_id = fields.Many2one(
        "pt.branch",
        string="الفرع | Branch",
        domain="[('clinic_company_id', '=', clinic_company_id)]",
        default=_default_branch_id,
        tracking=True,
    )
    birth_date = fields.Date(string="تاريخ الميلاد | DOB")
    age_years = fields.Integer(string="العمر | Age", compute="_compute_age_years", store=False)
    gender = fields.Selection(
        [("male", "ذكر | Male"), ("female", "أنثى | Female"), ("other", "أخرى | Other")],
        string="النوع | Gender",
        default="other",
    )
    national_id = fields.Char(string="الرقم القومي | National ID", tracking=True)
    governorate = fields.Selection(
        [
            ("damietta", "دمياط | Damietta"),
            ("dakahlia", "الدقهلية | Dakahlia"),
            ("cairo", "القاهرة | Cairo"),
            ("alexandria", "الإسكندرية | Alexandria"),
            ("other", "أخرى | Other"),
        ],
        string="المحافظة | Governorate",
        default="damietta",
    )
    phone = fields.Char(string="الهاتف | Phone", related="partner_id.phone", store=True, readonly=False)
    email = fields.Char(string="البريد الإلكتروني | Email", related="partner_id.email", store=True, readonly=False)
    whatsapp = fields.Char(string="واتساب | WhatsApp")
    job_title = fields.Char(string="الوظيفة | Job")
    primary_physician = fields.Char(string="الطبيب المحول | Primary Physician")
    emergency_contact = fields.Char(string="طوارئ | Emergency Contact")
    emergency_relation = fields.Char(string="صلة القرابة | Relation")
    medical_history = fields.Text(string="التاريخ المرضي | Medical History")
    allergy_notes = fields.Text(string="الحساسية | Allergy Notes")
    company_id = fields.Many2one(
        "res.partner", string="جهة العمل | Employer Company", domain=[("is_company", "=", True)]
    )
    active = fields.Boolean(string="نشط | Active", default=True)
    appointment_ids = fields.One2many("pt.appointment", "patient_id", string="المواعيد | Appointments")
    session_ids = fields.One2many("pt.session", "patient_id", string="الجلسات | Sessions")
    assessment_ids = fields.One2many("pt.assessment", "patient_id", string="التقييمات | Assessments")
    treatment_plan_ids = fields.One2many("pt.treatment.plan", "patient_id", string="الخطط العلاجية | Care Plans")
    therapy_sheet_ids = fields.One2many("pt.therapy.sheet", "patient_id", string="الملفات العلاجية | Therapy Sheets")

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
