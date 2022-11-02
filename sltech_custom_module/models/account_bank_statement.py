# -*- coding: utf-8 -*-
##############################################################################
#
#    SLTECH ERP SOLUTION
#    Copyright (C) 2020-Today(www.slecherpsolution.com).
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
import datetime

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError

class AccountBankStatement(models.Model):
    _inherit = "account.bank.statement"

    @api.model
    def default_get(self, fields_list):
        res = super(AccountBankStatement, self).default_get(fields_list)
        move_lines = self.env['account.move.line'].search([('journal_id', '=', res.get('journal_id')), ('reconciled', '=', False),
                                                           ('account_id', 'in', [self.env.user.company_id.account_journal_payment_debit_account_id.id,
                                                                                 self.env.user.company_id.account_journal_payment_credit_account_id.id]),
                                                           ('display_type', 'not in', ('line_section', 'line_note')),
                                                           ('parent_state', '!=', 'cancel'),
                                                           ])
        line_vals = []
        for line in move_lines:
            line_vals.append((0, 0, {
                'date': line.date,
                'payment_ref': line.move_id.ref if line.move_id.ref else line.move_id.name,
                'partner_id': line.move_id.partner_id.id,
                'amount': line.amount_currency,
                'journal_id': line.journal_id.id
            }))
        res.update({'line_ids': line_vals})
        return res



