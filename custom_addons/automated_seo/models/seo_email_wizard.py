from odoo import models, fields, api
from odoo.exceptions import UserError
import logging

_logger = logging.getLogger(__name__)


class SEOSendEmailWizard(models.Model):
    _name = 'seo.send.email.wizard'
    _description = 'SEO Preview Email Wizard'

    # recipient_ids = fields.Many2many(
    #     'res.users',
    #     'seo_email_recipient_rel',
    #     'wizard_id',
    #     'user_id',
    #     string='Recipients'
    # )
    # available_contributor_ids = fields.Many2many(
    #     'res.users',
    #     'seo_email_contributor_rel',
    #     'wizard_id',
    #     'user_id',
    #     string='Available Contributors'
    # )
    feedback = fields.Char(string='Feed Back', required=True)

    # @api.model
    # def default_get(self, fields):
    #     res = super(SEOSendEmailWizard, self).default_get(fields)
    #     active_id = self.env.context.get('active_id')
    #     if active_id:
    #         view = self.env['automated_seo.view'].browse(active_id)
    #         res.update({
    #             'available_contributor_ids': [(6, 0, view.contributor_ids.ids)],
    #         })
    #     return res

    def action_send_email(self):
        self.ensure_one()
        # if not self.recipient_ids:
        #     raise UserError('Please select at least one recipient.')


        active_id = self.env.context.get('active_id')
        view = self.env['automated_seo.view'].browse(active_id)
        view.message_post(
            body=f'Feedback : {self.feedback}',
            # partner_ids=self.recipient_ids.mapped('partner_id').ids,
        )
        view.stage = 'in_progress'
        view.active_version.stage = 'in_progress'

        return {
            'type': 'ir.actions.act_window_close',
            'infos': {
                'type': 'notification',
                'title': 'Success',
                'message': 'Feedback sent successfully',
                'sticky': False,
            }
        }
