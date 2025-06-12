from odoo import models, fields

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    bol_client_id = fields.Char(string="Bol Client ID", config_parameter="bol_inquiry_sync.client_id")
    bol_client_secret = fields.Char(string="Bol Client Secret", config_parameter="bol_inquiry_sync.client_secret")
    bol_access_token = fields.Char(string="Access Token", config_parameter="bol_inquiry_sync.access_token")