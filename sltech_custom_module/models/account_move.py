# -*- coding: utf-8 -*-
##############################################################################
#
#    SLTECH ERP SOLUTION
#    Copyright (C) 2022-Today(www.slecherpsolution.com).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
from odoo import api, fields, models, _, tools
from odoo.exceptions import UserError

class AccountMove(models.Model):
    _inherit = 'account.move'

    is_service_charge = fields.Boolean(string='Is Service Charge', default=False)
    service_amount_remaining = fields.Float('Amount Remaining', compute='sltech_compute_remaining_service_charge_amount', store=True)

    @api.depends('invoice_line_ids.sltech_price_unit')
    def sltech_compute_remaining_service_charge_amount(self):
        for rec in self:
            if rec.is_service_charge:
                rec.service_amount_remaining = sum((line.price_unit - line.sltech_price_unit) for line in rec.invoice_line_ids)

    @api.onchange('journal_id')
    def _change_is_service_charge(self):
        for res in self:
            if res.journal_id.id == res.env.ref('sltech_custom_module.sltech_service_charge_journal').id:
                res.is_service_charge = True
            else:
                res.is_service_charge = False


    def open_popup(self):

        lines = []
        for res in self:
            if res.is_service_charge or res.move_type != 'in_invoice':
                raise UserError(_(
                    "Can not select service charge invoices!!."
                ))
            if res.state not in ['posted']:
                raise UserError(_(
                    "Please select only posted invoices!!"
                ))
            for line in res.invoice_line_ids:
                lines.append((0, 0, {
                    'invoice_no': res.name,
                    'date': res.invoice_date,
                    'item_name': line.product_id.name,
                    'item_no': line.product_id.default_code,
                    'quantity': line.quantity,
                    'unit_price': line.price_unit,
                    'move_id': res.id,
                    'line_id': line.id,
                }))

        return {
            'type': 'ir.actions.act_window',
            'name': _('Amount Distribution'),
            'res_model': 'amount.distribution',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'active_model': 'account.move',
                'active_ids': self.ids,
                'default_distribution_line_ids': lines,
                'default_invoice_charge_ids': self.ids
            },
        }

class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    sltech_price_unit = fields.Float("Amount Already Used", copy=False)



class StockLandedCost(models.Model):
    _inherit = 'stock.landed.cost'

    def get_valuation_lines(self):
        lines = super(StockLandedCost, self).get_valuation_lines()
        stop_create_product_ids = self._context.get('product_ids')
        if stop_create_product_ids:
            for line in lines:
                if line['product_id'] in stop_create_product_ids:
                    lines.remove(line)
        return lines