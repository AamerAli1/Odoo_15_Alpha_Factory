# -*- coding: utf-8 -*-
from odoo import api, fields, models, _


class AccountMove(models.Model):
    _inherit = "account.move"

    discount_total = fields.Monetary("Discount Total",
                                     compute='total_discount')

    # Count the total discount
    @api.depends('invoice_line_ids.quantity', 'invoice_line_ids.price_unit',
                 'invoice_line_ids.discount')
    def total_discount(self):
        for invoice in self:
            total_price = 0
            discount_amount = 0
            final_discount_amount = 0
            if invoice:
                for line in invoice.invoice_line_ids:
                    if line:
                        total_price = line.quantity * line.price_unit
                        if total_price:
                            discount_amount = (line.price_total * line.discount) / 100
                            if discount_amount:
                                final_discount_amount += discount_amount
                invoice.update({'discount_total': final_discount_amount})
