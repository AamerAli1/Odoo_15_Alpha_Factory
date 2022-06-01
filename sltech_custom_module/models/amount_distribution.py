import datetime

from odoo import api, fields, models, _
from odoo.exceptions import UserError

class AmountDistribution(models.TransientModel):
    _name = "amount.distribution"

    service_charge_ids = fields.Many2many('account.move', string="Service Charge Ids")
    service_charge_line_ids = fields.One2many('service.charge.line', 'service_charge_id', 'Move Lines')
    distribution_line_ids = fields.One2many('amount.distribution.line', 'distribution_id', 'Distribution Line')

    @api.onchange('distribution_line_ids', 'service_charge_line_ids', 'service_charge_ids')
    def _compute_will_distribute_amount(self):
        total_amount = 0
        total_lines = 0
        for line in self.service_charge_line_ids:
            total_amount += line.amount_to_distribute

        for line in self.distribution_line_ids:
            if line.is_distribute:
                total_lines += 1

        for line in self.distribution_line_ids:
            amt = 0
            if line.is_distribute:
                amt = total_amount / total_lines
            line.update({'will_distribute_amount': amt})

    @api.onchange('service_charge_ids')
    def _on_service_charge_ids_selected(self):
        lines = [(5, 0)]
        for move_id in self.service_charge_ids.browse(self.service_charge_ids.ids):
            for line in move_id.invoice_line_ids:
                lines.append((0, 0, {
                    'product_id': line.product_id.id,
                    'slip_type': line.name,
                    'invoice_no': move_id.name,
                    'date': move_id.invoice_date,
                    'distribution_type': 'equal',
                    'amount': line.price_unit - line.sltech_price_unit,
                    'amount_to_distribute': line.price_unit - line.sltech_price_unit,
                    'line_id': line.id,
                }))
        self.service_charge_line_ids = lines

    def action_save(self):
        bill_ids = set([x.move_id for x in self.distribution_line_ids if x.is_distribute])
        service_lines = []
        for service_charge in self.service_charge_line_ids:
            service_lines.append((0, 0, {
                'product_id': service_charge.product_id,
                'quantity': 1,
                'price_unit': service_charge.amount_to_distribute,
                'is_landed_costs_line': True,
            }))
        for bill_id in bill_ids:
            no_distribute_products = [x.line_id.product_id.id for x in self.distribution_line_ids if x.move_id == bill_id and not x.is_distribute]
            sum_lines_price = sum([x.will_distribute_amount for x in self.distribution_line_ids if
                                      x.move_id == bill_id and x.is_distribute])
            # update price
            for service_line in service_lines:
                service_line[2]['price_unit'] = sum_lines_price

            is_created = bill_id.write({
                'invoice_line_ids': service_lines,
                'invoice_date': datetime.datetime.now()
            })
            if is_created:
                landed_costs_id = bill_id.button_create_landed_costs()
                landed_costs_obj = self.env['stock.landed.cost'].browse(landed_costs_id['res_id'])
                picking_ids = self.env['purchase.order'].search([('invoice_ids', 'in', bill_id.ids)]).picking_ids.ids

                landed_costs_obj.write({
                    'picking_ids': [(6, 0, picking_ids)]
                })
                landed_costs_obj = landed_costs_obj.with_context(product_ids=no_distribute_products)
                landed_costs_obj.button_validate()
        # amount distribute log
        for charge in self.service_charge_line_ids:
            current_price = charge.line_id.sltech_price_unit
            charge.line_id.update({
                'sltech_price_unit': current_price + charge.amount_to_distribute
            })


class AmountDistributionLine(models.TransientModel):
    _name = "amount.distribution.line"

    distribution_id = fields.Many2one('amount.distribution', 'Distribution Id')

    invoice_no = fields.Char("Invoice No")
    date = fields.Date("Date")
    item_name = fields.Char("Item Name")
    item_no = fields.Char("Item No")
    quantity = fields.Float("Quantity")
    unit_price = fields.Char("Unit Price")
    is_distribute = fields.Boolean("Is Distribute", default="True")
    move_id = fields.Many2one("account.move")
    line_id = fields.Many2one("account.move.line")
    will_distribute_amount = fields.Float("Will Distribute")



class ServiceChargeLine(models.TransientModel):
    _name = "service.charge.line"

    service_charge_id = fields.Many2one('amount.distribution', 'service charge Id')

    product_id = fields.Integer("Product id")
    slip_type = fields.Char("Slip Type")
    invoice_no = fields.Char("Invoice No")
    date = fields.Date("Date")
    distribution_type = fields.Selection(
        [
            ('equal', 'Equal'),
            ('by_quantity', 'By Quantity'),
            ('by_current_cost_price', 'By Current Cost'),
            ('by_weight', 'By Weight'),
            ('by_volume', 'By Volume'),
        ],
        string='Distribution Type',
        default="equal")
    amount = fields.Float("Amount")
    amount_to_distribute = fields.Float("Amount to Distribute")
    line_id = fields.Many2one("account.move.line")

    @api.onchange('amount_to_distribute')
    def _on_change_amount_to_distribute(self):
        if self.amount_to_distribute > self.amount:
            raise UserError(_("You cannot use amount to distribute more than amount"))