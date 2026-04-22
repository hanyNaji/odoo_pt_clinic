from odoo import api, fields, models
from odoo.exceptions import ValidationError

from ..domain.pricing import apply_discount, resolve_contract_price


class PtTreatmentPackage(models.Model):
    _name = "pt.treatment.package"
    _description = "Wiqaya Treatment Package"

    name = fields.Char(string="اسم الباقة | Package", required=True)
    patient_id = fields.Many2one("pt.patient", string="المريض | Patient", required=True, ondelete="restrict")
    clinic_company_id = fields.Many2one(
        "res.company", string="الشركة | Company", required=True, default=lambda self: self.env.company, index=True
    )
    branch_id = fields.Many2one(
        "pt.branch",
        string="الفرع | Branch",
        domain="[('clinic_company_id', '=', clinic_company_id)]",
    )
    company_id = fields.Many2one(
        "res.partner", string="شركة متعاقدة | Corporate Client", domain=[("is_company", "=", True)]
    )
    total_sessions = fields.Integer(string="إجمالي الجلسات | Total Sessions", required=True, default=10)
    used_sessions = fields.Integer(string="المستخدم | Used Sessions", compute="_compute_usage", store=True)
    remaining_sessions = fields.Integer(string="المتبقي | Remaining Sessions", compute="_compute_usage", store=True)
    start_date = fields.Date(string="تاريخ البداية | Start Date", default=fields.Date.context_today)
    end_date = fields.Date(string="تاريخ النهاية | End Date")
    billing_mode = fields.Selection(
        [("prepaid", "مدفوعة مقدما | Prepaid"), ("postpaid", "حسب الجلسات | Postpaid by Sessions")],
        string="نمط الفوترة | Billing Mode",
        default="prepaid",
        required=True,
    )
    base_price = fields.Float(string="السعر الأساسي | Base Price", required=True, default=0.0)
    discount_type = fields.Selection(
        [("none", "بدون | None"), ("percent", "نسبة | Percent"), ("fixed", "قيمة | Fixed")], string="نوع الخصم | Discount Type", default="none"
    )
    discount_value = fields.Float(string="قيمة الخصم | Discount Value", default=0.0)
    final_price = fields.Float(string="السعر النهائي | Final Price", compute="_compute_final_price", store=True)
    usage_ids = fields.One2many("pt.package.usage", "package_id", string="استخدام الجلسات | Usage")

    @api.constrains("total_sessions", "base_price", "discount_value")
    def _check_numbers(self):
        for record in self:
            if record.total_sessions <= 0:
                raise ValidationError("Total sessions must be greater than zero.")
            if record.base_price < 0:
                raise ValidationError("Base price cannot be negative.")
            if record.discount_type == "percent" and not 0 <= record.discount_value <= 100:
                raise ValidationError("Percent discount must be between 0 and 100.")
            if record.discount_type == "fixed" and record.discount_value < 0:
                raise ValidationError("Fixed discount cannot be negative.")

    @api.constrains("start_date", "end_date")
    def _check_dates(self):
        for record in self:
            if record.start_date and record.end_date and record.end_date < record.start_date:
                raise ValidationError("Package end date cannot be before start date.")

    @api.depends("usage_ids")
    def _compute_usage(self):
        for record in self:
            used = len(record.usage_ids)
            record.used_sessions = used
            record.remaining_sessions = max(record.total_sessions - used, 0)

    @api.depends("base_price", "discount_type", "discount_value")
    def _compute_final_price(self):
        for record in self:
            record.final_price = apply_discount(record.base_price, record.discount_type, record.discount_value)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            vals.setdefault("clinic_company_id", self.env.company.id)
            if vals.get("patient_id"):
                patient = self.env["pt.patient"].browse(vals["patient_id"])
                vals.setdefault("branch_id", patient.branch_id.id)
                vals["clinic_company_id"] = patient.clinic_company_id.id
        return super().create(vals_list)


class PtPackageUsage(models.Model):
    _name = "pt.package.usage"
    _description = "Wiqaya Package Session Usage"
    _order = "used_on desc"
    _session_uniq = models.Constraint(
        "unique(session_id)",
        "Session can be charged only once.",
    )

    package_id = fields.Many2one("pt.treatment.package", string="الباقة | Package", required=True, ondelete="cascade")
    session_id = fields.Many2one("pt.session", string="الجلسة | Session", required=True, ondelete="cascade")
    clinic_company_id = fields.Many2one(
        "res.company", string="الشركة | Company", related="package_id.clinic_company_id", store=True, index=True
    )
    used_on = fields.Date(string="تاريخ الاستخدام | Used On", required=True)


class PtDiscountOffer(models.Model):
    _name = "pt.discount.offer"
    _description = "Wiqaya Discount Offer"
    _code_company_uniq = models.Constraint(
        "unique(code, clinic_company_id)",
        "Offer code must be unique.",
    )

    name = fields.Char(string="اسم العرض | Offer", required=True)
    code = fields.Char(string="كود العرض | Offer Code", required=True)
    active = fields.Boolean(string="نشط | Active", default=True)
    clinic_company_id = fields.Many2one(
        "res.company", string="الشركة | Company", required=True, default=lambda self: self.env.company, index=True
    )
    branch_id = fields.Many2one(
        "pt.branch",
        string="الفرع | Branch",
        domain="[('clinic_company_id', '=', clinic_company_id)]",
    )
    offer_type = fields.Selection(
        [("percent", "نسبة | Percent"), ("fixed", "قيمة | Fixed")], string="نوع العرض | Offer Type", required=True, default="percent"
    )
    value = fields.Float(string="القيمة | Value", required=True)
    start_date = fields.Date(string="تاريخ البداية | Start Date")
    end_date = fields.Date(string="تاريخ النهاية | End Date")

    @api.constrains("offer_type", "value", "start_date", "end_date")
    def _check_offer_values(self):
        for record in self:
            if record.offer_type == "percent" and not 0 <= record.value <= 100:
                raise ValidationError("Offer percentage must be between 0 and 100.")
            if record.offer_type == "fixed" and record.value < 0:
                raise ValidationError("Fixed offer value cannot be negative.")
            if record.start_date and record.end_date and record.end_date < record.start_date:
                raise ValidationError("Offer end date cannot be before start date.")


class PtCompanyContract(models.Model):
    _name = "pt.company.contract"
    _description = "Wiqaya Company Contract"

    name = fields.Char(string="اسم العقد | Contract", required=True)
    clinic_company_id = fields.Many2one(
        "res.company", string="الشركة | Company", required=True, default=lambda self: self.env.company, index=True
    )
    branch_id = fields.Many2one(
        "pt.branch",
        string="الفرع | Branch",
        domain="[('clinic_company_id', '=', clinic_company_id)]",
    )
    partner_id = fields.Many2one(
        "res.partner", string="الجهة المتعاقدة | Corporate Partner", required=True, domain=[("is_company", "=", True)], ondelete="restrict"
    )
    start_date = fields.Date(string="تاريخ البداية | Start Date", required=True)
    end_date = fields.Date(string="تاريخ النهاية | End Date", required=True)
    state = fields.Selection(
        [("draft", "مسودة | Draft"), ("active", "نشط | Active"), ("expired", "منتهي | Expired")], string="الحالة | Status", default="draft"
    )
    line_ids = fields.One2many("pt.company.contract.line", "contract_id", string="بنود العقد | Contract Lines")

    @api.constrains("start_date", "end_date")
    def _check_dates(self):
        for record in self:
            if record.start_date and record.end_date and record.end_date < record.start_date:
                raise ValidationError("Contract end date cannot be before start date.")

    def action_activate(self):
        self.write({"state": "active"})


class PtCompanyContractLine(models.Model):
    _name = "pt.company.contract.line"
    _description = "Wiqaya Company Contract Line"

    contract_id = fields.Many2one("pt.company.contract", string="العقد | Contract", required=True, ondelete="cascade")
    clinic_company_id = fields.Many2one(
        "res.company", string="الشركة | Company", related="contract_id.clinic_company_id", store=True, index=True
    )
    product_id = fields.Many2one("product.product", string="الخدمة | Service", required=True, ondelete="restrict")
    fixed_price = fields.Float(string="سعر ثابت | Fixed Price")
    discount_percent = fields.Float(string="خصم % | Discount %")
    service_notes = fields.Char(string="ملاحظات الخدمة | Service Notes")


class PtSessionInvoicingWizard(models.TransientModel):
    _name = "pt.session.invoicing.wizard"
    _description = "Create invoice from Wiqaya sessions"

    patient_id = fields.Many2one("pt.patient", string="المريض | Patient", required=True)
    session_ids = fields.Many2many("pt.session", string="الجلسات | Sessions", domain="[(\"patient_id\",\"=\",patient_id), (\"billed\",\"=\",False)]")
    package_id = fields.Many2one("pt.treatment.package", string="الباقة | Package", domain="[(\"patient_id\",\"=\",patient_id)]")
    product_id = fields.Many2one("product.product", string="الخدمة | Service", required=True)
    unit_price = fields.Float(string="سعر الوحدة | Unit Price", required=True)
    discount_type = fields.Selection(
        [("none", "بدون | None"), ("percent", "نسبة | Percent"), ("fixed", "قيمة | Fixed")], string="نوع الخصم | Discount Type", default="none"
    )
    discount_value = fields.Float(string="قيمة الخصم | Discount Value", default=0.0)
    offer_id = fields.Many2one("pt.discount.offer", string="عرض الخصم | Discount Offer", domain="[(\"active\",\"=\",True)]")

    def action_create_invoice(self):
        self.ensure_one()
        partner = self.patient_id.partner_id
        qty = len(self.session_ids)
        today = fields.Date.context_today(self)
        if qty <= 0:
            raise ValidationError("Select at least one session.")

        effective_price = apply_discount(self.unit_price, self.discount_type, self.discount_value)

        if self.offer_id:
            if self.offer_id.start_date and self.offer_id.start_date > today:
                raise ValidationError("Selected discount offer is not active yet.")
            if self.offer_id.end_date and self.offer_id.end_date < today:
                raise ValidationError("Selected discount offer has expired.")
            effective_price = apply_discount(effective_price, self.offer_id.offer_type, self.offer_id.value)

        if self.package_id and self.package_id.billing_mode == "prepaid":
            effective_price = 0.0

        if self.patient_id.company_id:
            contract_line = self.env["pt.company.contract.line"].search(
                [
                    ("contract_id.partner_id", "=", self.patient_id.company_id.id),
                    ("contract_id.state", "=", "active"),
                    ("contract_id.start_date", "<=", today),
                    ("contract_id.end_date", ">=", today),
                    ("product_id", "=", self.product_id.id),
                ],
                limit=1,
            )
            if contract_line:
                effective_price = resolve_contract_price(
                    effective_price,
                    contract_line.fixed_price,
                    contract_line.discount_percent,
                )

        line_name = f"جلسات علاج طبيعي / Therapy Sessions x{qty} - {self.patient_id.name}"
        move = self.env["account.move"].create(
            {
                "move_type": "out_invoice",
                "partner_id": partner.id,
                "invoice_origin": "Wiqaya Session Billing",
                "invoice_line_ids": [
                    (
                        0,
                        0,
                        {
                            "product_id": self.product_id.id,
                            "quantity": qty,
                            "price_unit": effective_price,
                            "name": line_name,
                        },
                    )
                ],
            }
        )
        self.session_ids.write({"billed": True})
        return {
            "name": "Customer Invoice",
            "type": "ir.actions.act_window",
            "res_model": "account.move",
            "res_id": move.id,
            "view_mode": "form",
        }
