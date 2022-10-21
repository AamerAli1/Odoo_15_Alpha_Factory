# -*- coding: utf-8 -*-
{
    'name': "SW - Multi Currency Partner Ledger",
    'summary': """Partner Ledger report catering for multiple currency transactions""",
    'author': "Smart Way Business Solutions",
    'website': "https://www.smartway.co",
    'license':  "Other proprietary",
    'category': 'Accounting',
    'version': '13.0.1.1',
    'depends': ['base', 'account', 'account_reports'],
    'data': ['wizard/account_report_partner_ledger_view.xml',
             'report/report_partnerledger.xml',
             'report/web_external_layout.xml',
             ],
    'images':  ["static/description/image.png"],
    'price': 80,
    'currency' :  'EUR',
    'installable': True
}
