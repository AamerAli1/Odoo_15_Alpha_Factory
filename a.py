from datetime import datetime
import xmlrpc.client
import ssl
ssl._create_default_https_context = ssl._create_unverified_context

# in local
db = "Alpha_221007"  # Database name
odoo_username = "developer"  # odoo username
odoo_password = "developer"  # odoo password
url = 'http://localhost:8069' # odoo url/domain can work with https
# end

common = xmlrpc.client.ServerProxy(url+"/xmlrpc/2/common")
uid = common.authenticate(db, odoo_username, odoo_password, {})
models = xmlrpc.client.ServerProxy("{}/xmlrpc/2/object".format(url))


payment_ids = models.execute_kw(
        db,
        uid,
        odoo_password,
        "account.payment",
        "search_read",
        [],
        {
            'fields': ['id', 'payment_type'],
            # 'offset': offset*1000,
            # 'limit': 20
            'order': 'id asc'
        })
for s in payment_ids:
    payment_type = s.get('payment_type', '')
    code = ''
    if payment_type == 'inbound':
        code = 'account.payment.customer.invoice'
    elif payment_type == 'outbound':
        code = 'account.payment.supplier.invoice'

    payment_seq = models.execute_kw(db, uid, odoo_password, "ir.sequence", 'next_by_code', [], {
        'sequence_code': code
    })
    models.execute_kw(db, uid, odoo_password, "account.payment", 'write', [[s['id']], {
        'sltech_name': payment_seq
    }])
    print("Updated Payment Sequence: "+str(s))
