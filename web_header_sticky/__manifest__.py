# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright Domiup (<http://domiup.com>).
#
##############################################################################

{
    'name': 'List View and One2many Header Sticky',
    'version': '17.0.1.0',
    'category': 'Web',
    'description': """
Header of List View and One2many List View are sticked when rolling
    """,
    'summary': '''
Header of List View and One2many List View are sticked when rolling
    ''',
    'live_test_url': 'https://demo13.domiup.com',
    'author': 'Domiup',
    'price': 0,
    'currency': 'EUR',
    'license': 'OPL-1',
    'support': 'domiup.contact@gmail.com',
    # 'website': 'https://youtu.be/Bsmjch5A73Y',
    'depends': [
        'web',
    ],
    "assets": {
        "web.assets_backend": [
            "web_header_sticky/static/src/scss/base.scss",
        ],
    },
    'test': [],
    'demo': [],
    'images': ['static/description/banner.png'],
    'installable': True,
    'active': False,
    'application': False,
}
