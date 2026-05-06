from odoo import fields, models


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
        self.env.cr.execute(
            """
            SELECT udt_name
              FROM information_schema.columns
             WHERE table_name = 'pt_branch'
               AND column_name = 'name'
            """
        )
        column_info = self.env.cr.fetchone()
        if column_info and column_info[0] != "jsonb":
            self.env.cr.execute(
                """
                ALTER TABLE pt_branch
                ALTER COLUMN name TYPE jsonb
                USING CASE
                    WHEN name IS NULL THEN NULL
                    ELSE jsonb_build_object('en_US', name::text)
                END
                """
            )

    code = fields.Char(string="Branch Code", required=True)
    clinic_company_id = fields.Many2one(
        "res.company", string="Company", required=True, default=lambda self: self.env.company, index=True
    )
    manager_id = fields.Many2one("res.users", string="Branch Manager")
    phone = fields.Char(string="Phone")
    email = fields.Char(string="Email")
    address = fields.Char(string="Address")
    active = fields.Boolean(string="Active", default=True)

