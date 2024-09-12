# -*- coding: utf-8 -*-
from importlib.metadata import files

from odoo import models, fields, api
from odoo.fields import Many2one


class Offer(models.Model):
    _name = 'automed_seo.offers'
    _description = 'Offers data'


    title = fields.Char(string = "Offer Title")
    description = fields.Text()
    benefits = fields.One2many('automed_seo.offer_benefits', inverse_name='offer_id',string='Offers benefits')



class OfferBenefit(models.Model):

    _name = 'automed_seo.offer_benefits'
    _description = 'Offer benefits'
    _rec_name = 'benefit_title'

    offer_id = fields.Many2one('automed_seo.offers',string="Related offer-id")
    benefit_title = fields.Char(string='Benefit title')

    def _compute_display_name(self):
        for benefit in self:
            benefit.display_name = f"{benefit.benefit_title}"

