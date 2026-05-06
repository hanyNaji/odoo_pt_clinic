from odoo import api, fields, models
from odoo.exceptions import ValidationError


class PtAppointment(models.Model):
    _name = "pt.appointment"
    _description = "Wiqaya Appointment"
    _order = "start_datetime desc"
    _inherit = ["pt.reminder.mixin"]

    name = fields.Char(string="Appointment", required=True, default="Therapy Session")
    patient_id = fields.Many2one("pt.patient", string="Patient", required=True, ondelete="restrict", index=True)
    clinic_company_id = fields.Many2one(
        "res.company", string="Company", required=True, default=lambda self: self.env.company, index=True
    )
    branch_id = fields.Many2one(
        "pt.branch",
        string="Branch",
        domain="[('clinic_company_id', '=', clinic_company_id)]",
        index=True,
    )
    therapist_id = fields.Many2one(
        "res.users", string="Therapist", required=True, default=lambda self: self.env.user, index=True
    )
    assistant_id = fields.Many2one("res.users", string="Reception", index=True)
    treatment_type = fields.Selection(
        [
            ("evaluation", "Initial Evaluation"),
            ("manual", "Manual Therapy"),
            ("exercise", "Exercise Therapy"),
            ("electro", "Electrotherapy"),
            ("followup", "Follow-up"),
        ],
        string="Treatment Type",
        default="followup",
        required=True,
    )
    start_datetime = fields.Datetime(string="Start", required=True, index=True)
    end_datetime = fields.Datetime(string="End", required=True, index=True)
    status = fields.Selection(
        [
            ("draft", "Draft"),
            ("confirmed", "Confirmed"),
            ("done", "Done"),
            ("cancelled", "Cancelled"),
            ("no_show", "No Show"),
        ],
        string="Status",
        default="draft",
        index=True,
    )
    room = fields.Char(string="Room")
    notes = fields.Text(string="Notes")
    session_id = fields.Many2one("pt.session", string="Session", readonly=True, index=True)
    reminder_sent = fields.Boolean(string="Reminder Sent", default=False, readonly=True)
    reminder_sent_at = fields.Datetime(string="Reminder Sent At", readonly=True)

    @api.onchange("patient_id")
    def _onchange_patient_id(self):
        for record in self:
            if record.patient_id:
                record.branch_id = record.patient_id.branch_id
                record.clinic_company_id = record.patient_id.clinic_company_id

    @api.constrains("start_datetime", "end_datetime")
    def _check_datetime(self):
        for record in self:
            if record.start_datetime and record.end_datetime and record.end_datetime <= record.start_datetime:
                raise ValidationError("End time must be after start time.")

    @api.constrains("start_datetime", "end_datetime", "therapist_id", "status")
    def _check_therapist_overlap(self):
        for record in self:
            if not (record.start_datetime and record.end_datetime and record.therapist_id):
                continue
            conflict_count = self.search_count(
                [
                    ("id", "!=", record.id),
                    ("therapist_id", "=", record.therapist_id.id),
                    ("status", "in", ["draft", "confirmed"]),
                    ("start_datetime", "<", record.end_datetime),
                    ("end_datetime", ">", record.start_datetime),
                ]
            )
            if conflict_count:
                raise ValidationError("This therapist already has another appointment in the same time slot.")

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            vals.setdefault("clinic_company_id", self.env.company.id)
            vals.setdefault("reminder_sent", False)
            if not vals.get("branch_id") and vals.get("patient_id"):
                patient = self.env["pt.patient"].browse(vals["patient_id"])
                vals["branch_id"] = patient.branch_id.id
                vals["clinic_company_id"] = patient.clinic_company_id.id
        return super().create(vals_list)

    def write(self, vals):
        if "start_datetime" in vals or "patient_id" in vals:
            vals["reminder_sent"] = False
            vals["reminder_sent_at"] = False
        return super().write(vals)

    def action_confirm(self):
        self.write({"status": "confirmed"})

    def action_done(self):
        for record in self:
            if not record.session_id:
                record.action_create_session()
            record.status = "done"

    def action_cancel(self):
        self.write({"status": "cancelled"})

    def action_no_show(self):
        self.write({"status": "no_show"})

    def _build_reminder_message(self):
        self.ensure_one()
        start_txt = fields.Datetime.context_timestamp(self, self.start_datetime).strftime("%Y-%m-%d %H:%M")
        branch = self.branch_id.name or "Main Branch"
        return f"تذكير بموعد العلاج الطبيعي للمريض {self.patient_id.name} يوم {start_txt} في {branch}."

    def _send_gateway_reminder(self, channel, gateway_url, recipient, message):
        payload = {
            "channel": channel,
            "to": recipient,
            "message": message,
            "appointment_id": self.id,
            "patient_code": self.patient_id.code,
        }
        ok, response_text = self._post_gateway_message(gateway_url, payload)
        self.env["pt.reminder.log"].create(
            {
                "appointment_id": self.id,
                "patient_id": self.patient_id.id,
                "channel": channel,
                "recipient": recipient,
                "payload": str(payload),
                "status": "sent" if ok else "failed",
                "response_text": response_text,
            }
        )
        return ok

    @api.model
    def cron_send_appointment_reminders(self):
        icp = self.env["ir.config_parameter"].sudo()
        sms_gateway = icp.get_param("pt_clinic.sms_gateway_url", default="")
        wa_gateway = icp.get_param("pt_clinic.whatsapp_gateway_url", default="")

        start_at, end_at = self._get_reminder_window()
        candidates = self.search(
            [
                ("status", "in", ["draft", "confirmed"]),
                ("reminder_sent", "=", False),
                ("start_datetime", ">=", start_at),
                ("start_datetime", "<=", end_at),
            ]
        )

        for appointment in candidates:
            recipient = appointment.patient_id.whatsapp or appointment.patient_id.phone
            if not recipient:
                continue

            message = appointment._build_reminder_message()
            delivered = False
            if wa_gateway:
                delivered = appointment._send_gateway_reminder("whatsapp", wa_gateway, recipient, message)
            if sms_gateway and not delivered:
                delivered = appointment._send_gateway_reminder("sms", sms_gateway, recipient, message)

            if delivered:
                appointment.write({"reminder_sent": True, "reminder_sent_at": fields.Datetime.now()})

    def action_create_session(self):
        self.ensure_one()
        if self.session_id:
            return {
                "type": "ir.actions.act_window",
                "name": "Session",
                "res_model": "pt.session",
                "res_id": self.session_id.id,
                "view_mode": "form",
                "target": "current",
            }

        session = self.env["pt.session"].create(
            {
                "name": self.name,
                "patient_id": self.patient_id.id,
                "appointment_id": self.id,
                "therapist_id": self.therapist_id.id,
                "session_datetime": self.start_datetime,
                "duration_minutes": max(int((self.end_datetime - self.start_datetime).total_seconds() / 60), 1),
                "clinic_company_id": self.clinic_company_id.id,
                "branch_id": self.branch_id.id,
            }
        )
        self.write({"session_id": session.id, "status": "done"})
        return {
            "type": "ir.actions.act_window",
            "name": "Session",
            "res_model": "pt.session",
            "res_id": session.id,
            "view_mode": "form",
            "target": "current",
        }
