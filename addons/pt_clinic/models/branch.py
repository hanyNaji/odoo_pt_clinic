from odoo import fields, models


class PtBranch(models.Model):
    _name = "pt.branch"
    _description = "Wiqaya Physiotherapy Branch"
    _order = "name"
    _code_company_uniq = models.Constraint(
        "unique(code, clinic_company_id)",
        "Branch code must be unique per company.",
    )

    name = fields.Char(string="الفرع | Branch", required=True)
    code = fields.Char(string="كود الفرع | Branch Code", required=True)
    clinic_company_id = fields.Many2one(
        "res.company", string="الشركة | Company", required=True, default=lambda self: self.env.company, index=True
    )
    manager_id = fields.Many2one("res.users", string="مدير الفرع | Branch Manager")
    phone = fields.Char(string="الهاتف | Phone")
    email = fields.Char(string="البريد الإلكتروني | Email")
    address = fields.Char(string="العنوان | Address")
    active = fields.Boolean(string="نشط | Active", default=True)


