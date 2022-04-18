from odoo import models, fields

class productTemplate(models.Model):
    _inherit="product.template"


    reference = fields.Char(string="Reference")
    hsCode = fields.Char(string="HS Code")

    product_group_name = fields.Char(string="Group Name")

class PurchaseReport(models.Model):
    _inherit = "purchase.report"

    product_group_name = fields.Char(string="Group Name", readonly=True)

    def _select(self):
        return super(PurchaseReport, self)._select() + ", t.product_group_name as product_group_name"

    def _group_by(self):
        return super(PurchaseReport, self)._group_by() + ", t.product_group_name"


class SaleReport(models.Model):
    _inherit = "sale.report"

    po_no = fields.Char()

    product_group_name = fields.Char(string="Group Name", readonly=True)

    def _query(self, with_clause='', fields={}, groupby='', from_clause=''):
        fields['product_group_name'] = ", t.product_group_name as product_group_name"
        groupby += ", t.product_group_name"
        return super(SaleReport, self)._query(with_clause, fields, groupby, from_clause)