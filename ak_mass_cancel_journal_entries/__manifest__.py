# -*- coding: utf-8 -*-
# Part of Odoo, Aktiv Software.
# See LICENSE file for full copyright & licensing details.
# Author: Aktiv Software.
# mail: odoo@aktivsoftware.com
# Copyright (C) 2015-Present Aktiv Software PVT. LTD.
# Contributions:
# Aktiv Software:
# - Viral Zala
# - Chirag Patel
# - Harshil Soni
{
    'name': "Mass Cancel Journal Entries",
    'summary': """ This module allows to cancel or delete mass/bulk/multiple Journal Entries
            from the tree view.""",
    'author': "Aktiv Software",
    'website': "http://www.aktivsoftware.com",
    'category': 'Accounting',
    'version': '15.0.1.0.0',
    'license': 'OPL-1',
    "currency": "EUR",
    "price": "10",

    # any module necessary for this one to work correctly
    'depends': ['account'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'wizard/journal_entries_cancel_wizard.xml',
    ],
    'images': ['static/description/banner.png'],
    'installable': True,
    'auto_install': False,
}
