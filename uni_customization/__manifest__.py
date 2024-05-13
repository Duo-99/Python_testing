# -*- coding: utf-8 -*-
{
    'name': "uni_customization",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        Long description of module's purpose
    """,

    'author': "My Company",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'stock', 'repair', 'sale', 'account', 'purchase', 'report_py3o', 'account_dynamic_reports',
                'product_expiry', 'auditlog', 'stock_landed_costs'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'security/security.xml',
        'views/views.xml',
        'views/templates.xml',
        'views/stock_picking_views.xml',
        'views/repair_order.xml',
        'views/sale_order_views.xml',
        'views/menuitem_view.xml',
        'views/product_template.xml',
        'views/product_brand_view.xml',
        'views/ca_category_views.xml',
        'views/order_type_view.xml',
        'views/account_move.xml',
        'views/purchase_views.xml',
        'views/res_partner.xml',
        # 'report/sale_order_spec_report.xml',
        'demo/demo.xml',
        'views/stock_quant_views.xml',
        'views/product_pricelist.xml',
        # 'views/res_users.xml',
        'views/account_payment.xml',
        'views/stock_orderpoint_view.xml',
        'views/stock_location_view.xml',
        'views/stock_landed_cost.xml',
        'report/picking_operation_report.xml',
        'views/account_bank_statement.xml',
        'views/stock_valuation_layer_views.xml'
    ],
    # only loaded in demonstration mode

    'assets': {
        'web.assets_backend': [
            'uni_customization/static/src/js/custom_partner_ageing.js',
        ],
        'web.assets_qweb': [
            'uni_customization/static/src/xml/custom_partner_ageing.xml',
        ]
    },
    'qweb': ['static/src/xml/custom_partner_ageing.xml'],
}
