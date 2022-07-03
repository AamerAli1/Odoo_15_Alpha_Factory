import datetime

from odoo import api, fields, models, _
from odoo.exceptions import UserError

class AmountDistribution(models.TransientModel):
    _name = "amount.distribution"

    service_charge_ids = fields.Many2many('account.move', string="Service Charge Ids")
    invoice_charge_ids = fields.Many2many('account.move', 'invoice_charge_ids_rel', 'col1', 'col2', string="Invoice Charge Ids")
    service_charge_line_ids = fields.One2many('service.charge.line', 'service_charge_id', 'Move Lines')
    distribution_line_ids = fields.One2many('amount.distribution.line', 'distribution_id', 'Distribution Line')

    @api.onchange('distribution_line_ids', 'service_charge_line_ids', 'service_charge_ids')
    def _compute_will_distribute_amount(self):
        line_dict_is_approve = {}
        total_qty_is_approve = 0
        total_weight_is_approve = 0
        total_volume_is_approve = 0
        total_current_cost_price_is_approve = 0
        for line in self.distribution_line_ids:
            if line.is_distribute:
                line_dict_is_approve[line] = [0.0,0.0,0.0,0.0,0.0]    #  [equal, by_quantity, by_current_cost_price, by_weight, by_volume]
                total_qty_is_approve += line.quantity
                total_weight_is_approve += line.weight
                total_volume_is_approve += line.volume
                total_current_cost_price_is_approve += line.former_cost

        for line in self.service_charge_line_ids:

            # by_current_cost_price_qty
            # by_weight_qty
            # by_volume_qty
            'by_current_cost_price'
            'by_weight'
            'by_volume'
            if line.distribution_type == 'equal':
                amt = line.amount_to_distribute / len(line_dict_is_approve)
                for ln in line_dict_is_approve:
                    line_dict_is_approve[ln][0] = line_dict_is_approve[ln][0] + amt
                    ln.update({
                        'will_distribute_amount': sum(line_dict_is_approve[ln]),
                        'equal_qty': line_dict_is_approve[ln][0]
                    })
            elif line.distribution_type == 'by_quantity':
                amt = line.amount_to_distribute / total_qty_is_approve
                for ln in line_dict_is_approve:
                    line_dict_is_approve[ln][1] = line_dict_is_approve[ln][1] + amt*ln.quantity
                    ln.update({
                        'will_distribute_amount': sum(line_dict_is_approve[ln]),
                        'by_quantity_qty': line_dict_is_approve[ln][1]
                    })
            elif line.distribution_type == 'by_current_cost_price':
                amt = 0
                if total_current_cost_price_is_approve != 0:
                    amt = line.amount_to_distribute / total_current_cost_price_is_approve
                for ln in line_dict_is_approve:
                    line_dict_is_approve[ln][2] = line_dict_is_approve[ln][2] + amt*ln.quantity
                    ln.update({
                        'will_distribute_amount': sum(line_dict_is_approve[ln]),
                        'by_current_cost_price_qty': line_dict_is_approve[ln][2]
                    })
            elif line.distribution_type == 'by_weight':
                amt = 0
                if total_weight_is_approve != 0:
                    amt = line.amount_to_distribute / total_weight_is_approve
                for ln in line_dict_is_approve:
                    line_dict_is_approve[ln][3] = line_dict_is_approve[ln][3] + amt*ln.weight
                    ln.update({
                        'will_distribute_amount': sum(line_dict_is_approve[ln]),
                        'by_weight_qty': line_dict_is_approve[ln][3]
                    })
            elif line.distribution_type == 'by_volume':
                amt = 0
                if total_volume_is_approve != 0:
                    amt = line.amount_to_distribute / total_volume_is_approve
                for ln in line_dict_is_approve:
                    line_dict_is_approve[ln][4] = line_dict_is_approve[ln][4] + amt*ln.volume
                    ln.update({
                        'will_distribute_amount': sum(line_dict_is_approve[ln]),
                        'by_volume_qty': line_dict_is_approve[ln][4]
                    })






        # total_amount = 0
        # total_lines = 0
        # for line in self.service_charge_line_ids:
        #     total_amount += line.amount_to_distribute
        #
        # for line in self.distribution_line_ids:
        #     if line.is_distribute:
        #         total_lines += 1

        # for line in self.distribution_line_ids:
        #     amt = 0
        #     if line.is_distribute:
        #         amt = total_amount / total_lines
        #     line.update({'will_distribute_amount': amt})

    @api.onchange('service_charge_ids')
    def _on_service_charge_ids_selected(self):
        lines = [(5, 0)]
        for move_id in self.service_charge_ids.browse(self.service_charge_ids.ids):
            for line in move_id.invoice_line_ids:
                if (line.price_unit - line.sltech_price_unit) > 0:
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

    @api.onchange('invoice_charge_ids')
    def _on_invoice_charge_ids_selected(self):
        lines = [(5, 0)]
        for move_id in self.invoice_charge_ids.browse(self.invoice_charge_ids.ids):
            for line in move_id.invoice_line_ids:
                lines.append((0, 0, {
                    'invoice_no': move_id.name,
                    'date': move_id.invoice_date,
                    'item_name': line.product_id.name,
                    'item_no': line.product_id.default_code,
                    'quantity': line.quantity,
                    'unit_price': line.price_unit,
                    'move_id': move_id.id,
                    'line_id': line.id,
                }))
        self.distribution_line_ids = lines

    def action_save(self):
        if self.service_charge_line_ids:
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

                cost_lines = []
                for l in self.service_charge_line_ids:
                    price_unit = 0
                    split_method = ''
                    if l.distribution_type == 'equal':
                        split_method = 'equal'
                        price_unit = sum([x.equal_qty for x in self.distribution_line_ids if
                                        x.move_id == bill_id and x.is_distribute])
                    elif l.distribution_type == 'by_quantity':
                        split_method = 'by_quantity'
                        price_unit = sum([x.by_quantity_qty for x in self.distribution_line_ids if
                                        x.move_id == bill_id and x.is_distribute])
                    elif l.distribution_type == 'by_current_cost_price':
                        split_method = 'by_current_cost_price'
                        price_unit = sum([x.by_current_cost_price_qty for x in self.distribution_line_ids if
                                        x.move_id == bill_id and x.is_distribute])
                    elif l.distribution_type == 'by_weight':
                        split_method = 'by_weight'
                        price_unit = sum([x.by_weight_qty for x in self.distribution_line_ids if
                                        x.move_id == bill_id and x.is_distribute])
                    elif l.distribution_type == 'by_volume':
                        split_method = 'by_volume'
                        price_unit = sum([x.by_volume_qty for x in self.distribution_line_ids if
                                        x.move_id == bill_id and x.is_distribute])
                    if price_unit != 0:
                        cost_lines.append((0, 0, {
                            'product_id': l.product_id.id,
                            'name': l.product_id.name,
                            'account_id': l.line_id.account_id.id,
                            'price_unit': price_unit,
                            'split_method': split_method,
                        }))
                if cost_lines:
                    landed_costs = self.env['stock.landed.cost'].create({
                        'vendor_bill_id': bill_id.id,
                        'cost_lines': cost_lines,
                    })


                    landed_costs_obj = self.env['stock.landed.cost'].browse(landed_costs.id)
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

            for rec in self.service_charge_ids:
                rec.service_amount_remaining = sum(
                    (line.price_unit - line.sltech_price_unit) for line in rec.invoice_line_ids)


class AmountDistributionLine(models.TransientModel):
    _name = "amount.distribution.line"

    distribution_id = fields.Many2one('amount.distribution', 'Distribution Id')

    invoice_no = fields.Char("Invoice No")
    date = fields.Date("Date")
    item_name = fields.Char("Item Name")
    item_no = fields.Char("Item No")
    quantity = fields.Float("Quantity")
    weight = fields.Float("Weight")
    volume = fields.Float("Volume")
    former_cost = fields.Float("Current Cost")
    unit_price = fields.Char("Unit Price")
    is_distribute = fields.Boolean("Is Distribute", default="True")
    move_id = fields.Many2one("account.move")
    line_id = fields.Many2one("account.move.line")
    will_distribute_amount = fields.Float("Will Distribute")

    equal_qty = fields.Float()
    by_quantity_qty = fields.Float()
    by_current_cost_price_qty = fields.Float()
    by_weight_qty = fields.Float()
    by_volume_qty = fields.Float()



class ServiceChargeLine(models.TransientModel):
    _name = "service.charge.line"

    service_charge_id = fields.Many2one('amount.distribution', 'service charge Id')

    product_id = fields.Many2one("product.product")
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