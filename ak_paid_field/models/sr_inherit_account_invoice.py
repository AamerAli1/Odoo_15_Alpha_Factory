# -*- coding: utf-8 -*-
##############################################################################
#
#    This module uses OpenERP, Open Source Management Solution Framework.
#    Copyright (C) 2017-Today Sitaram
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>
#
##############################################################################


from odoo import models, fields, api, _

class AccountMove(models.Model):
    _inherit='account.move'

    amount_paid = fields.Monetary(string='Paid Amount In FC', readonly=True, compute='_compute_paid_amount')
    amount_paid_signed = fields.Monetary(string='Paid Amount In SAR', readonly=True, compute='_compute_paid_amount')
   



    def _compute_paid_amount(self):
        for record in self:
            record.amount_paid = record.amount_total - record.amount_residual
            record.amount_paid_signed = record.amount_total_signed - record.amount_residual_signed

