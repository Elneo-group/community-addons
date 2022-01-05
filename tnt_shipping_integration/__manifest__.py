# -*- coding: utf-8 -*-pack
{
    # App information
    'name': 'TNT Odoo Shipping Integration',
    'category': 'Website',
    'author': "Vraja Technologies",
    'version': '13.16.03.2020',
    'summary': """Using TNT Easily manage Shipping Operation in odoo.Export Order While Validate Delivery Order.Import Tracking From TNT to odoo.Generate Label in odoo.We also Provide the mrw,gls,mondial relay,fedex shipping integration.""",
    'description': """""",
    'depends': ['delivery'],
    'data': ['views/res_comapny.xml',
             'views/delivery_carrier.xml',
             'views/stock_picking.xml',],
    'images': ['static/description/cover.jpg'],
    'maintainer': 'Vraja Technologies',
    'website': 'www.vrajatechnologies.com',
    'demo': [],
    'live_test_url': 'http://www.vrajatechnologies.com/contactus',
    'installable': True,
    'application': True,
    'auto_install': False,
    'price': '299',
    'currency': 'EUR',
    'license': 'OPL-1',
}

# version changelog
# _ 14.16.03.2020 __ Initial version of the app
