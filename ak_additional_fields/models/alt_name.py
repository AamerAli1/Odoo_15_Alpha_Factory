from odoo import models, api, _, _lt, fields

class Partnerpage(models.Model):
    _inherit = 'res.partner'

    altName = fields.Char(string="Alternative Name")
    partnerCode = fields.Char(string="Code")


