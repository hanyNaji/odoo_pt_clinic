import json
from datetime import timedelta
from urllib import error, request

from odoo import api, fields, models


class PtReminderLog(models.Model):
    _name = "pt.reminder.log"
    _description = "PT Appointment Reminder Log"
    _order = "create_date desc"

    appointment_id = fields.Many2one("pt.appointment", required=True, ondelete="cascade")
    patient_id = fields.Many2one("pt.patient", required=True, ondelete="cascade")
    channel = fields.Selection([("sms", "SMS"), ("whatsapp", "WhatsApp")], required=True)
    recipient = fields.Char(required=True)
    payload = fields.Text()
    status = fields.Selection([("sent", "Sent"), ("failed", "Failed")], required=True)
    response_text = fields.Text()


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    pt_reminder_hours_before = fields.Integer(string="PT Reminder Hours", default=24)
    pt_sms_gateway_url = fields.Char(string="PT SMS Gateway URL")
    pt_whatsapp_gateway_url = fields.Char(string="PT WhatsApp Gateway URL")

    def set_values(self):
        super().set_values()
        icp = self.env["ir.config_parameter"].sudo()
        icp.set_param("pt_clinic.reminder_hours_before", self.pt_reminder_hours_before or 24)
        icp.set_param("pt_clinic.sms_gateway_url", self.pt_sms_gateway_url or "")
        icp.set_param("pt_clinic.whatsapp_gateway_url", self.pt_whatsapp_gateway_url or "")

    @api.model
    def get_values(self):
        res = super().get_values()
        icp = self.env["ir.config_parameter"].sudo()
        res.update(
            pt_reminder_hours_before=int(icp.get_param("pt_clinic.reminder_hours_before", default="24")),
            pt_sms_gateway_url=icp.get_param("pt_clinic.sms_gateway_url", default=""),
            pt_whatsapp_gateway_url=icp.get_param("pt_clinic.whatsapp_gateway_url", default=""),
        )
        return res


class PtReminderMixin(models.AbstractModel):
    _name = "pt.reminder.mixin"
    _description = "Reminder Sender Mixin"

    def _post_gateway_message(self, url, payload):
        req = request.Request(
            url=url,
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with request.urlopen(req, timeout=10) as resp:
                return True, resp.read().decode("utf-8")
        except error.URLError as ex:
            return False, str(ex)

    def _get_reminder_window(self):
        hours = int(
            self.env["ir.config_parameter"].sudo().get_param("pt_clinic.reminder_hours_before", default="24")
        )
        now = fields.Datetime.now()
        return now, now + timedelta(hours=hours)

