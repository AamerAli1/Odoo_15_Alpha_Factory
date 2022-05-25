# -*- coding: utf-8 -*-

# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models, api, _, _lt, fields
from odoo.tools.misc import format_date
from datetime import timedelta


# class StockMove(models.Model):
# 	_inherit = 'stock.move'

# 	consumed_lot_ids = fields.Many2many('stock.production.lot', string="Consumed Lots", copy=False)
# 	consumed_lot_name = fields.Char(string='Consumed Lots', compute="_compute_lot_name", copy=False)

# 	def _compute_lot_name(self):
# 		for move in self:
# 			consumed_lot_name = ''
# 			if move.consumed_lot_ids:
# 				lot_list = move.consumed_lot_ids.mapped('name')
# 				consumed_lot_name = ', '.join(lot_list)
# 			move.update({
# 				'consumed_lot_name' : consumed_lot_name
# 			})


class MrpProduction(models.Model):
	""" Manufacturing Orders """
	_inherit = 'mrp.production'


	customer_name_mrporder = fields.Char(string="Customer Name", related="bom_id.customer_name_bom")

	# def action_assign(self):
	# 	result = super(MrpProduction, self).action_assign()

	# 	for production in self:
	# 		for move in production.move_raw_ids:
	# 			lot_ids = move.move_line_ids.mapped('lot_id')
	# 			move.write({
	# 				'consumed_lot_ids' : [(6,0,lot_ids.ids)]
	# 			})
	# 	return result

class MrpBom(models.Model):
	_inherit = 'mrp.bom'
	customer_name_bom = fields.Char(string = 'Customer Name')



# class MrpProductProduce(models.TransientModel):
# 	_inherit = "mrp.production"

# 	def do_produce(self):
# 		for line in self:
# 			active_model = self._context.get('active_model')
# 			active_id = self._context.get('active_id')
# 			record_id = self.env[active_model].browse(active_id)
# 			produced_lines = line._workorder_line_ids()
# 			for move in record_id.move_raw_ids:
# 				move_line = produced_lines.filtered(lambda x : x.product_id == move.product_id)
# 				move.write({
# 					'consumed_lot_ids' : [(6,0,move_line.mapped("lot_id").ids)]
# 				})
# 		return super(MrpProductProduce, self).do_produce()
