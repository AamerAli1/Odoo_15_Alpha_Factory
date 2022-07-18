from odoo import models, api, _, _lt, fields

class Partnerpage(models.Model):
    _inherit = 'business.appointment'

    checkin = fields.Char(string="Alternative Name")
    partnerCode = fields.Boolean(string="Check in")


