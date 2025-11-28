import datetime
from odoo import fields, models


class ResUsers(models.Model):
    _inherit = "res.users"

    def activity_update_role_reminder(self):
        reports_activity_unlink = self.env['res.users']
        activity_type_xmlid = 'base_user_role_activity.mail_activity_role_expire'
        for user in self:
            expiring_lines = user.role_line_ids.filtered_domain(self.env["res.users.role.line"]._get_reminder_days_domain())
            if expiring_lines:
                activity_type_id = self.env['ir.model.data']._xmlid_to_res_id(activity_type_xmlid, raise_if_not_found=False)
                activity_type = self.env['mail.activity.type'].browse(activity_type_id)
                user.partner_id.activity_schedule(
                    activity_type_id=activity_type_id,
                    date_deadline = min(expiring_lines.mapped('date_to')),
                    note= activity_type.default_note % { 
                        "user": user.self._get_html_link(), 
                        "roles": "<br/>-".join([f"{line.role_id.name} ({line.date_to})" for line in expiring_lines])
                    },
                    user_id=user.employee_parent_id.user_id.id or user.id)
            else:
                reports_activity_unlink |= user
        if reports_activity_unlink:
            reports_activity_unlink.mapped("partner_id").activity_unlink([activity_type_xmlid])