{
    "name": "Bol.com Klantvragen Sync",
    "version": "1.0",
    "category": "Helpdesk",
    "summary": "Synchroniseer bol.com klantvragen als Odoo Helpdesk-tickets",
    "depends": ["helpdesk"],
    "data": [
        "data/cron.xml",
        "security/ir.model.access.csv",
        "views/res_config_settings_views.xml",
        "views/bol_inquiry_views.xml"
    ],
    "installable": True,
    "application": False,
}