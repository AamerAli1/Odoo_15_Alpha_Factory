# -*- coding: utf-8 -*-
##############################################################################
#
#    SLTECH ERP SOLUTION
#    Copyright (C) 2022-Today(www.slecherpsolution.com).

##############################################################################
{
        'name': "SL TECH - Custom Module",
        'description': 'Custom Module',
        'data': [
                'security/ir.model.access.csv',
                'data/journal_data.xml',
                'views/account_move.xml',
                'views/amount_distribution.xml',
        ],
        'author': "SL TECH ERP SOLUTION",
        'website': "https://www.sltecherpsolution.com",
        'category': 'Uncategorized',
        'version': '0.1',
        'license': 'Other proprietary',

        'depends': [
                'sale',
                'purchase',
                'account',
                'stock_landed_costs'
        ],

}
