from odoo import api, fields, models
from odoo.exceptions import ValidationError


class PtAssessment(models.Model):
    _name = "pt.assessment"
    _description = "Wiqaya Assessment"
    _order = "assessment_date desc, id desc"

    name = fields.Char(string="اسم التقييم | Assessment", required=True)
    patient_id = fields.Many2one("pt.patient", string="المريض | Patient", required=True, ondelete="restrict", index=True)
    clinic_company_id = fields.Many2one(
        "res.company", string="الشركة | Company", required=True, default=lambda self: self.env.company, index=True
    )
    branch_id = fields.Many2one(
        "pt.branch",
        string="الفرع | Branch",
        domain="[('clinic_company_id', '=', clinic_company_id)]",
    )
    therapist_id = fields.Many2one("res.users", string="المعالج | Therapist", required=True, default=lambda self: self.env.user, index=True)
    assessment_date = fields.Date(string="تاريخ التقييم | Assessment Date", required=True, default=fields.Date.context_today, index=True)
    patient_code = fields.Char(string="MRN / ID", related="patient_id.code", store=False)
    patient_age = fields.Integer(string="العمر | Age", related="patient_id.age_years", store=False)
    patient_gender = fields.Selection(related="patient_id.gender", string="النوع | Gender", store=False)
    primary_physician = fields.Char(string="الطبيب المحول | Primary Physician", related="patient_id.primary_physician", store=False)
    chief_complaints = fields.Text(string="الشكوى الرئيسية | Chief Complaints")
    diagnosis = fields.Text(string="التشخيص | Diagnosis", required=True)
    history_present_illness = fields.Text(string="تاريخ الحالة الحالية والسابق | History of Present / Past Illness")
    onset = fields.Char(string="بداية الحالة | Onset")
    course = fields.Char(string="مسار الحالة | Course")
    condition_diabetes = fields.Boolean(string="Diabetes")
    condition_hypertension = fields.Boolean(string="Hypertension")
    condition_infections = fields.Boolean(string="Infections")
    condition_heart_disease = fields.Boolean(string="Heart diseases")
    condition_osteoporosis = fields.Boolean(string="Osteoporosis")
    condition_skin_disease = fields.Boolean(string="Skin diseases")
    condition_convulsions = fields.Boolean(string="Convulsions")
    condition_other = fields.Char(string="حالات أخرى | Other Conditions")
    operations_history = fields.Text(string="العمليات | Operations")
    allergies_history = fields.Text(string="الحساسية | Allergies")
    investigation_mri = fields.Boolean(string="MRI")
    investigation_ct = fields.Boolean(string="CT")
    investigation_xray = fields.Boolean(string="X-Ray")
    investigation_ultrasound = fields.Boolean(string="Ultrasound (US)")
    investigation_emg_ncs = fields.Boolean(string="EMG/NCS")
    finding = fields.Text(string="نتيجة الفحص | Finding")
    pain_score = fields.Integer(string="درجة الألم | Pain Score")
    findings = fields.Text(string="ملاحظات الفحص | Additional Findings")
    red_flags = fields.Text(string="محاذير / Precautions | Red Flags / Precautions")
    functional_limitations = fields.Text(string="القيود الوظيفية | Functional Limitations")
    goals_patient_therapist = fields.Text(string="الأهداف | Goals (Patient & Therapist)")
    recommendations = fields.Text(string="التوصيات | Recommendations")

    @api.constrains("pain_score")
    def _check_pain_score(self):
        for record in self:
            if record.pain_score is not None and not 0 <= record.pain_score <= 10:
                raise ValidationError("Pain score must be between 0 and 10.")

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            vals.setdefault("clinic_company_id", self.env.company.id)
            if vals.get("patient_id"):
                patient = self.env["pt.patient"].browse(vals["patient_id"])
                vals.setdefault("branch_id", patient.branch_id.id)
                vals["clinic_company_id"] = patient.clinic_company_id.id
            if not vals.get("name") and vals.get("patient_id"):
                patient = self.env["pt.patient"].browse(vals["patient_id"])
                vals["name"] = f"Assessment - {patient.name}"
        return super().create(vals_list)


class PtTreatmentPlan(models.Model):
    _name = "pt.treatment.plan"
    _description = "Wiqaya Treatment Plan"
    _order = "plan_date desc, id desc"

    name = fields.Char(string="اسم الخطة | Treatment Plan", required=True)
    patient_id = fields.Many2one("pt.patient", string="المريض | Patient", required=True, ondelete="restrict", index=True)
    clinic_company_id = fields.Many2one(
        "res.company", string="الشركة | Company", required=True, default=lambda self: self.env.company, index=True
    )
    branch_id = fields.Many2one(
        "pt.branch",
        string="الفرع | Branch",
        domain="[('clinic_company_id', '=', clinic_company_id)]",
    )
    therapist_id = fields.Many2one("res.users", string="المعالج | Therapist", required=True, default=lambda self: self.env.user, index=True)
    plan_date = fields.Date(string="تاريخ الخطة | Plan Date", required=True, default=fields.Date.context_today, index=True)
    plan_time = fields.Char(string="الوقت | Time")
    start_date = fields.Date(string="تاريخ البداية | Start Date", required=True, default=fields.Date.context_today, index=True)
    end_date = fields.Date(string="تاريخ النهاية | End Date", index=True)
    patient_gender = fields.Selection(related="patient_id.gender", string="النوع | Gender", store=False)
    patient_age = fields.Integer(related="patient_id.age_years", string="العمر | Age", store=False)
    patient_pin = fields.Char(string="PIN", related="patient_id.code", store=False)

    finding_pain = fields.Boolean(string="Pain")
    finding_restricted_rom = fields.Boolean(string="Restricted ROM")
    finding_disturbed_balance = fields.Boolean(string="Disturbed balance")
    finding_affected_functional_ability = fields.Boolean(string="Affected functional ability")
    finding_disturbed_sensorimotor_control = fields.Boolean(string="Disturbed sensorimotor control")
    finding_lack_coordination = fields.Boolean(string="Lack of coordination")
    finding_muscle_weakness = fields.Boolean(string="Muscle weakness")
    finding_muscle_spasm = fields.Boolean(string="Muscle spasm")
    finding_lack_flexibility = fields.Boolean(string="Lack of flexibility")
    finding_affected_locomotion = fields.Boolean(string="Affected locomotion ability")
    finding_affected_posture = fields.Boolean(string="Affected posture")
    finding_affected_foot_deformity = fields.Boolean(string="Affected foot deformity")
    finding_edema = fields.Boolean(string="Edema")
    findings_other = fields.Char(string="Other Findings")

    goal_reduce_edema = fields.Boolean(string="Reduce edema")
    goal_reduce_pain = fields.Boolean(string="Reduce pain")
    goal_reduce_stiffness = fields.Boolean(string="Reduce stiffness")
    goal_reduce_muscle_spasm = fields.Boolean(string="Reduce muscle spasm")
    goal_reduce_disability = fields.Boolean(string="Reduce disability")
    goal_improve_adl = fields.Boolean(string="Improve ADL")
    goal_improve_balance = fields.Boolean(string="Improve balance")
    goal_improve_functional_ability = fields.Boolean(string="Improve functional ability")
    goal_improve_coordination = fields.Boolean(string="Improve coordination ability")
    goal_improve_gait = fields.Boolean(string="Improve gait pattern")
    goal_improve_circulation = fields.Boolean(string="Improve circulation")
    goal_improve_muscle_power = fields.Boolean(string="Improve muscle power")
    goal_improve_rom = fields.Boolean(string="Improve range of motion")
    goal_improve_weight_bearing = fields.Boolean(string="Improve weight bearing control")
    goal_prevent_deformities = fields.Boolean(string="Prevent deformities")
    goal_prevent_contracture = fields.Boolean(string="Prevent contracture")
    goal_prevent_muscle_wasting = fields.Boolean(string="Prevent muscle wasting")
    goals_other = fields.Char(string="Other Goals")

    modality_active_assisted_rom = fields.Boolean(string="Active assisted ROM")
    modality_passive_rom = fields.Boolean(string="Passive ROM")
    modality_isometric = fields.Boolean(string="Isometric strengthening")
    modality_stretching = fields.Boolean(string="Stretching exercises")
    modality_balance_exercises = fields.Boolean(string="Balance exercises")
    modality_postural_correction = fields.Boolean(string="Postural correction")
    modality_mulligan = fields.Boolean(string="Mulligan")
    modality_mckenzie = fields.Boolean(string="McKenzie")
    modality_stabilization = fields.Boolean(string="Stabilization")
    modality_mobilization = fields.Boolean(string="Mobilization")
    modality_myofascial_release = fields.Boolean(string="Myofascial release massage")
    modality_deep_friction = fields.Boolean(string="Deep friction massage")
    modality_plyometric = fields.Boolean(string="Plyometric exercises")
    modality_open_chain = fields.Boolean(string="Open chain exercises")
    modality_closed_chain = fields.Boolean(string="Closed chain exercises")
    modality_aerobic = fields.Boolean(string="Aerobic exercises")
    modality_resistance_band = fields.Boolean(string="Resistance band exercises")
    patient_education_given = fields.Boolean(string="Patient education given")
    home_exercise_plan = fields.Boolean(string="Home exercise care plan")
    modality_tens = fields.Boolean(string="TENS")
    modality_ultrasound = fields.Boolean(string="Ultrasound")
    modality_hot = fields.Boolean(string="Hot")
    modality_laser = fields.Boolean(string="Laser")
    modality_k_tape = fields.Boolean(string="K-tape")
    modality_pneumatic = fields.Boolean(string="Pneumatic")
    modality_leg_press = fields.Boolean(string="Leg press")
    modality_leg_curl = fields.Boolean(string="Leg curl")
    modalities_other = fields.Char(string="Other Modalities")

    goals = fields.Text(string="الأهداف الحرة | Goals Summary")
    interventions = fields.Text(string="التدخلات الحرة | Interventions Summary")
    status = fields.Selection(
        [("draft", "مسودة | Draft"), ("active", "نشطة | Active"), ("completed", "مكتملة | Completed")],
        string="الحالة | Status",
        default="draft",
    )
    session_ids = fields.One2many("pt.session", "treatment_plan_id", string="الجلسات | Sessions")

    @api.constrains("start_date", "end_date")
    def _check_dates(self):
        for record in self:
            if record.start_date and record.end_date and record.end_date < record.start_date:
                raise ValidationError("Treatment plan end date cannot be before start date.")

    def action_activate(self):
        self.write({"status": "active"})

    def action_complete(self):
        self.write({"status": "completed"})

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            vals.setdefault("clinic_company_id", self.env.company.id)
            vals.setdefault("plan_date", fields.Date.context_today(self))
            if vals.get("patient_id"):
                patient = self.env["pt.patient"].browse(vals["patient_id"])
                vals.setdefault("branch_id", patient.branch_id.id)
                vals["clinic_company_id"] = patient.clinic_company_id.id
            if not vals.get("name") and vals.get("patient_id"):
                patient = self.env["pt.patient"].browse(vals["patient_id"])
                vals["name"] = f"Care Plan - {patient.name}"
        return super().create(vals_list)


class PtSession(models.Model):
    _name = "pt.session"
    _description = "Wiqaya Session"
    _order = "session_datetime desc"

    name = fields.Char(string="اسم الجلسة | Session", required=True, default="جلسة علاج | Therapy Session")
    patient_id = fields.Many2one("pt.patient", string="المريض | Patient", required=True, ondelete="restrict", index=True)
    clinic_company_id = fields.Many2one(
        "res.company", string="الشركة | Company", required=True, default=lambda self: self.env.company, index=True
    )
    branch_id = fields.Many2one(
        "pt.branch",
        string="الفرع | Branch",
        domain="[('clinic_company_id', '=', clinic_company_id)]",
    )
    appointment_id = fields.Many2one("pt.appointment", string="الموعد | Appointment", ondelete="set null")
    treatment_plan_id = fields.Many2one("pt.treatment.plan", string="الخطة العلاجية | Treatment Plan", ondelete="set null")
    therapy_sheet_id = fields.Many2one("pt.therapy.sheet", string="الملف العلاجي | Therapy Sheet", ondelete="set null")
    therapist_id = fields.Many2one("res.users", string="المعالج | Therapist", required=True, default=lambda self: self.env.user, index=True)
    session_datetime = fields.Datetime(string="تاريخ الجلسة | Session Date", required=True, default=fields.Datetime.now, index=True)
    duration_minutes = fields.Integer(string="المدة بالدقائق | Duration", default=45)
    pain_before = fields.Integer(string="الألم قبل الجلسة | Pain Before")
    pain_after = fields.Integer(string="الألم بعد الجلسة | Pain After")
    subjective_notes = fields.Text(string="Subjective")
    objective_notes = fields.Text(string="Objective")
    assessment_notes = fields.Text(string="Assessment")
    plan_notes = fields.Text(string="Plan")
    package_id = fields.Many2one("pt.treatment.package", string="الباقة | Package", ondelete="set null")
    billed = fields.Boolean(string="تمت الفوترة | Billed", default=False, index=True)

    @api.onchange("appointment_id")
    def _onchange_appointment_id(self):
        for record in self:
            if record.appointment_id:
                record.patient_id = record.appointment_id.patient_id
                record.therapist_id = record.appointment_id.therapist_id
                record.session_datetime = record.appointment_id.start_datetime
                record.branch_id = record.appointment_id.branch_id
                record.clinic_company_id = record.appointment_id.clinic_company_id

    @api.onchange("patient_id")
    def _onchange_patient_id(self):
        for record in self:
            if record.patient_id and not record.appointment_id:
                record.branch_id = record.patient_id.branch_id
                record.clinic_company_id = record.patient_id.clinic_company_id

    @api.constrains("pain_before", "pain_after")
    def _check_pain_scores(self):
        for record in self:
            if record.pain_before is not None and not 0 <= record.pain_before <= 10:
                raise ValidationError("Pain before must be between 0 and 10.")
            if record.pain_after is not None and not 0 <= record.pain_after <= 10:
                raise ValidationError("Pain after must be between 0 and 10.")

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            appointment_id = vals.get("appointment_id")
            if appointment_id:
                appointment = self.env["pt.appointment"].browse(appointment_id)
                vals.setdefault("patient_id", appointment.patient_id.id)
                vals.setdefault("therapist_id", appointment.therapist_id.id)
                vals.setdefault("session_datetime", appointment.start_datetime)
                vals.setdefault("branch_id", appointment.branch_id.id)
                vals.setdefault("clinic_company_id", appointment.clinic_company_id.id)
            elif vals.get("patient_id"):
                patient = self.env["pt.patient"].browse(vals["patient_id"])
                vals.setdefault("branch_id", patient.branch_id.id)
                vals.setdefault("clinic_company_id", patient.clinic_company_id.id)

            package_id = vals.get("package_id")
            session_datetime = vals.get("session_datetime")
            if package_id:
                package = self.env["pt.treatment.package"].browse(package_id)
                if package.remaining_sessions <= 0:
                    raise ValidationError("Selected package has no remaining sessions.")
                if package.end_date and session_datetime:
                    session_date = fields.Datetime.to_datetime(session_datetime).date()
                    if session_date > package.end_date:
                        raise ValidationError("Selected package is expired for this session date.")

        records = super().create(vals_list)
        for record in records:
            if record.appointment_id:
                record.appointment_id.session_id = record.id
                record.appointment_id.status = "done"
            if record.package_id:
                used_on = fields.Datetime.to_datetime(record.session_datetime).date()
                self.env["pt.package.usage"].create(
                    {
                        "package_id": record.package_id.id,
                        "session_id": record.id,
                        "used_on": used_on,
                    }
                )
        return records


class PtTherapySheet(models.Model):
    _name = "pt.therapy.sheet"
    _description = "Wiqaya Physical Therapy Sheet"
    _order = "sheet_date desc, id desc"

    name = fields.Char(string="اسم الملف | Sheet Name", required=True)
    patient_id = fields.Many2one("pt.patient", string="المريض | Patient", required=True, ondelete="restrict", index=True)
    clinic_company_id = fields.Many2one(
        "res.company", string="الشركة | Company", required=True, default=lambda self: self.env.company, index=True
    )
    branch_id = fields.Many2one(
        "pt.branch",
        string="الفرع | Branch",
        domain="[('clinic_company_id', '=', clinic_company_id)]",
    )
    therapist_id = fields.Many2one("res.users", string="المعالج | Therapist", default=lambda self: self.env.user, index=True)
    sheet_date = fields.Date(string="تاريخ الملف | Sheet Date", required=True, default=fields.Date.context_today, index=True)
    case_type = fields.Selection(
        [("acute", "Acute"), ("chronic", "Chronic"), ("protective", "Protective")],
        string="نوع الحالة | Case Type",
        default="acute",
    )
    patient_age = fields.Integer(string="العمر | Age", related="patient_id.age_years", store=False)
    patient_job = fields.Char(string="الوظيفة | Job", related="patient_id.job_title", store=False)
    complaint = fields.Text(string="الشكوى | Complaint")
    diagnosis = fields.Text(string="التشخيص | Diagnosis")
    treatment_program = fields.Text(string="برنامج العلاج | Treatment Program")
    signature_name = fields.Char(string="التوقيع | Signature")
    line_ids = fields.One2many("pt.therapy.sheet.line", "sheet_id", string="السجل اليومي | Daily Log")

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            vals.setdefault("clinic_company_id", self.env.company.id)
            vals.setdefault("sheet_date", fields.Date.context_today(self))
            if vals.get("patient_id"):
                patient = self.env["pt.patient"].browse(vals["patient_id"])
                vals.setdefault("branch_id", patient.branch_id.id)
                vals["clinic_company_id"] = patient.clinic_company_id.id
                vals.setdefault("name", f"Physical Therapy Sheet - {patient.name}")
        return super().create(vals_list)


class PtTherapySheetLine(models.Model):
    _name = "pt.therapy.sheet.line"
    _description = "Wiqaya Physical Therapy Sheet Line"
    _order = "line_date desc, id desc"

    sheet_id = fields.Many2one("pt.therapy.sheet", string="الملف | Sheet", required=True, ondelete="cascade")
    clinic_company_id = fields.Many2one(
        "res.company", string="الشركة | Company", related="sheet_id.clinic_company_id", store=True, index=True
    )
    session_id = fields.Many2one("pt.session", string="الجلسة | Session", ondelete="set null")
    reference_code = fields.Char(string="ID", required=True)
    line_date = fields.Date(string="Date", required=True, default=fields.Date.context_today)
    case_name = fields.Char(string="Case Name", required=True)

    @api.onchange("session_id")
    def _onchange_session_id(self):
        for record in self:
            if record.session_id:
                record.reference_code = record.session_id.patient_id.code or record.reference_code
                record.line_date = fields.Datetime.to_datetime(record.session_id.session_datetime).date()
                record.case_name = record.session_id.name

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("sheet_id") and not vals.get("reference_code"):
                sheet = self.env["pt.therapy.sheet"].browse(vals["sheet_id"])
                vals["reference_code"] = sheet.patient_id.code or "N/A"
            if vals.get("session_id") and not vals.get("case_name"):
                session = self.env["pt.session"].browse(vals["session_id"])
                vals["case_name"] = session.name
                vals.setdefault("reference_code", session.patient_id.code or "N/A")
                vals.setdefault("line_date", fields.Datetime.to_datetime(session.session_datetime).date())
        return super().create(vals_list)
