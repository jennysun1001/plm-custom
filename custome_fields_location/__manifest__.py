#-*- coding: utf-8 -*-
{
    'name': "custome_fields_location",
    'summary': """Change location of some field """,
    'description': """ Change location of some field """,
    'author': "A2A Digital",
    'category': 'Extra Tools',
    'version': '14.0.1.0.0',
    'depends': [
            'stock_landed_costs',
            'purchase',
            'sale',
            ],
    'data': [
        'views/landed_cost_view.xml',
        'views/purchase_warehouse_view.xml',
    ],
}