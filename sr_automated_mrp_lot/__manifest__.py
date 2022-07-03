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

{
    'name': "Sitaram MRP Lot",
    'version': "13.0.0.0",
    'summary': "",
    'category': 'Extra Addons',
    'description': """
        Sitaram MRP Lot
    """,
    'author': "Sitaram",
    'website':"www.sitaramsolutions.in",
    'depends': ['base', 'sale', 'sale_management',
        'account', 'account_accountant', 'account_reports','mrp'],
    'data': [
        # 'views/stock_move_view.xml',
	    'views/mrp_customer_view.xml',
        'views/bom_customer_view.xml',
	    'reports/ak_mrp_workorder_report.xml',
        'views/manufacture_view.xml',


    ],
    'demo': [],
    "external_dependencies": {},
    "license": "AGPL-3",
    'installable': True,
    'auto_install': False,

}
