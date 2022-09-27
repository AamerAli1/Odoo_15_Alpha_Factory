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

class AccountPayment(models.Model):
    _inherit = "account.payment"

    sltech_name = fields.Char('Payment Reference', readonly=True)

    @api.model
    def create(self, vals):
        payment_type = vals.get('payment_type', '')
        code = ''
        if payment_type == 'outbound':
            code = 'account.payment.customer.invoice'
        elif payment_type == 'inbound':
            code = 'account.payment.supplier.invoice'
        if code:
            vals['sltech_name'] = self.env['ir.sequence'].next_by_code(code)
        return super(AccountPayment, self).create(vals)