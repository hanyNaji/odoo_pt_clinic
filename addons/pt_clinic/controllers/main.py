from odoo import fields, http
from odoo.http import request


class PtClinicApiController(http.Controller):
    @http.route("/pt/api/my_appointments", type="jsonrpc", auth="user", methods=["POST"], csrf=False)
    def my_appointments(self):
        appointments = request.env["pt.appointment"].search(
            [("therapist_id", "=", request.env.user.id)], order="start_datetime desc", limit=50
        )
        return [
            {
                "id": rec.id,
                "patient": rec.patient_id.name,
                "start": fields.Datetime.to_string(rec.start_datetime),
                "end": fields.Datetime.to_string(rec.end_datetime),
                "status": rec.status,
            }
            for rec in appointments
        ]

    @http.route("/pt/api/patient_sessions", type="jsonrpc", auth="user", methods=["POST"], csrf=False)
    def patient_sessions(self, patient_id):
        try:
            patient_id = int(patient_id)
        except (TypeError, ValueError):
            return []

        patient = request.env["pt.patient"].search([("id", "=", patient_id)], limit=1)
        if not patient:
            return []

        sessions = request.env["pt.session"].search([("patient_id", "=", patient.id)], order="session_datetime desc", limit=100)
        return [
            {
                "id": rec.id,
                "date": fields.Datetime.to_string(rec.session_datetime),
                "therapist": rec.therapist_id.name,
                "billed": rec.billed,
            }
            for rec in sessions
        ]

