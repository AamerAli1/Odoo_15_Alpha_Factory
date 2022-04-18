
{
    'name': "Additonal fields",
    'version': "15.0.0.1",
    'summary': "Additional fields",
    'category': 'Extra Addons',
    'description': """
        This app will add alternative name and code to partners
        and Reference,Barcode, and HS Code to Products
    """,
    'author': "Expertsintech",
    'website':"www.expertsintech.com",
    'depends': ['base','stock', 'purchase', 'sale', ],
    'data': [
      'views/altNameView.xml',
      'views/productTemplateView.xml',
      'views/invoice_fields_view.xml'


    ],
    'demo': [],
    "external_dependencies": {},
    "license": "AGPL-3",
    'installable': True,
    'auto_install': False,

}
