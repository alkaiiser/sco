{
    "name": "SCO HVAC Starter Component Bridge",
    "version": "19.0.1.1.1",
    "summary": "Staged component requirements for approved HVAC sales",
    "category": "Inventory",
    "license": "AGPL-3",
    "depends": [
        "sale_management",
        "purchase_stock",
        "sco_hvac_starter_boq",
        "sco_hvac_starter_oem",
        "sco_hvac_starter_controls",
        "sco_hvac_sales_engineering",
    ],
    "data": [
        "security/purchase_requirement_security.xml",
        "security/ir.model.access.csv",
        "views/component_bridge_views.xml",
        "views/purchase_requirement_views.xml",
    ],
    "installable": True,
    "application": False,
    "author": "SCO Technologies",
}
