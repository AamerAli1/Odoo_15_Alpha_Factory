from odoo import api, fields, models, _, tools

class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    order_line_id=fields.Many2one('sale.order.line','Previous Price')
    order_line_ids=fields.Many2many('sale.order.line','sale_order_line_order_lines','order_line_id','old_order_line_id',string='Previous Price')

    @api.onchange('product_id')
    def product_id_change(self):
        result = super(SaleOrderLine, self).product_id_change()
        if self.product_id and self.order_id.partner_id:
            if self.id:
                self._cr.execute('''
                                    SELECT id
                                    FROM sale_order_line
                                    WHERE product_id = %s
                                      AND state in ('sale','done')
                                      AND order_partner_id =%s
                                      AND id != %s
                                    order by id desc limit 5''',
                                       (self.product_id.id, self.order_id.partner_id.id,self.id))
            else:
                self._cr.execute('''
                                    SELECT id
                                    FROM sale_order_line
                                    WHERE product_id = %s
                                      AND state in ('sale','done')
                                      AND order_partner_id =%s
                                    order by id desc limit 5 ''',
                                       (self.product_id.id, self.order_id.partner_id.id))
            res=self._cr.fetchall()
            if not res:
                self.order_line_ids=[]
            else:
                self.order_line_ids=[(6,0, [r[0] for r in res])]
        else:
            self.order_line_ids=[]
        return result

    @api.onchange('order_line_id')
    def order_line_id_change(self):
        if self.order_line_id:
            self.price_unit=self.order_line_id.price_unit


    def name_get(self):
        result = []
        for so_line in self.sudo():
            name = '%s' % (so_line.price_unit)
            result.append((so_line.id, name))
        return result