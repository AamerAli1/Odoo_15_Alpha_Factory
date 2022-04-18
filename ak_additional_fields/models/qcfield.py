from odoo import models, api, _, _lt, fields

class Partnerpage(models.Model):
    _inherit = 'mrp.production'

    def calculateSplit(self):
        self.splitresult = self.product_qty / self.split_number
        return True


    split_number = fields.Float(String = "Number of Splits" , default = 1)



    splitresult = fields.Float(compute = calculateSplit)





    grinding_quality = fields.Char(string="Grinding Quality")
    viscosity = fields.Char(string="Viscosity")
    delta_e = fields.Char(string="Delta E")
    respName = fields.Char(string="Name")


class stock_move(models.Model):
    _inherit = 'stock.move'

    def split_quantity_cal(self):
        print("----------------------------------------------------------------------------")
        print(self.product_uom_qty)
        print(self.raw_material_production_id)
        return self.product_uom_qty / self.raw_material_production_id.split_number




