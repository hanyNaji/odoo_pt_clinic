from odoo import fields, models

from ..hooks import migrate_translated_char_columns


class PtBranch(models.Model):
    _name = "pt.branch"
    _description = "Wiqaya Physiotherapy Branch"
    _order = "name"
    _code_company_uniq = models.Constraint(
        "unique(code, clinic_company_id)",
        "Branch code must be unique per company.",
    )

    name = fields.Char(string="Branch", required=True, translate=True)

    def init(self):
        super().init()
        migrate_translated_char_columns(self.env)

    code = fields.Char(string="Branch Code", required=True)
    clinic_company_id = fields.Many2one(
        "res.company", string="Company", required=True, default=lambda self: self.env.company, index=True
    )
    manager_id = fields.Many2one("res.users", string="Branch Manager")
    phone = fields.Char(string="Phone")
    email = fields.Char(string="Email")
    address = fields.Char(string="Address")
    active = fields.Boolean(string="Active", default=True)

