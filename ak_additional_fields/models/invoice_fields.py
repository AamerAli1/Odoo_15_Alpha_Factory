from odoo import models, api, _, _lt, fields

class Partnerpage(models.Model):
    _inherit = 'account.move'
    vendor_po = fields.Char(string="client PO Number")
    branch_name = fields.Char(string = "Branch Name")


class invoiceLine(models.Model):
    _inherit = 'account.move.line'
    additional_description = fields.Char(string = "Description", store= True,index = True)