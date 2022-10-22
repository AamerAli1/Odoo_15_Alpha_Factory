# -*- coding: utf-8 -*-
##############################################################################
#
#    SLTECH ERP SOLUTION
#    Copyright (C) 2022-Today(www.slecherpsolution.com).

##############################################################################
{
        'name': "SL TECH - Custom Payment Sequence",
        'description': 'Custom Payment Sequence',
        'data': [
                'data/data.xml',
                'views/account_payment.xml',
                'report/payment_report.xml',
        ],
        'author': "SL TECH ERP SOLUTION",
        'website': "https://www.sltecherpsolution.com",
        'category': 'Uncategorized',
        'version': '0.1',
        'license': 'Other proprietary',

        'depends': [
                'account'
        ],

}
