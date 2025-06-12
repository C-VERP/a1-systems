import requests
from odoo import models, fields, tools
from datetime import datetime

class BolInquiry(models.Model):
    _name = "bol.inquiry"
    _description = "Bol.com Klantvraag"

    sync_log = fields.Text(string="Laatste Synchronisatie Log")
    sync_last_run = fields.Datetime(string="Laatste Uitvoering")

    inquiry_id = fields.Char(string="Bol Inquiry ID", required=True, index=True)
    customer_name = fields.Char(string="Klantnaam")
    email = fields.Char(string="E-mail")
    question = fields.Text(string="Vraag")
    date_created = fields.Datetime(string="Aangemaakt op")
    helpdesk_ticket_id = fields.Many2one("helpdesk.ticket", string="Helpdesk Ticket")


class BolInquirySync(models.Model):
    _inherit = 'bol.inquiry'

    def _get_bol_access_token(self):
        return self.env['ir.config_parameter'].sudo().get_param("bol_inquiry_sync.access_token")

    def _cron_fetch_inquiries(self):
        self.ensure_one()
        log = []
        token = self._get_bol_access_token()
        if not token:
            return

        headers = {
            "Accept": "application/vnd.retailer.v9+json",
            "Authorization": f"Bearer {token}"
        }
        url = "https://api.bol.com/retailer/inquiries"

        try:
            log.append('Ophalen gestart')
            response = requests.get(url, headers=headers, timeout=30)
            response.raise_for_status()
            data = response.json()

            for item in data.get("inquiries", []):
                inquiry_id = item.get("id")
                if self.env["bol.inquiry"].search([("inquiry_id", "=", inquiry_id)], limit=1):
                    continue  # Already imported

                log.append(f'Nieuw ticket aangemaakt voor {item.get("customerName")}')
                helpdesk_ticket = self.env["helpdesk.ticket"].create({
                    "name": f"Bol.com vraag van {item.get('customerName')}",
                    "description": item.get("question"),
                })

                self.create({
                    "inquiry_id": inquiry_id,
                    "customer_name": item.get("customerName"),
                    "email": item.get("customerEmail"),
                    "question": item.get("question"),
                    "date_created": item.get("dateTimeInquiry"),
                    "helpdesk_ticket_id": helpdesk_ticket.id,
                })

            self.write({'sync_log': '\n'.join(log), 'sync_last_run': datetime.now()})

        except Exception as e:
            _logger = tools.logging.getLogger(__name__)
            _logger.error("Fout bij synchronisatie: %s", str(e))


class BolOAuthToken(models.Model):
    _inherit = 'bol.inquiry'

    def _refresh_bol_access_token(self):
        client_id = self.env['ir.config_parameter'].sudo().get_param("bol_inquiry_sync.client_id")
        client_secret = self.env['ir.config_parameter'].sudo().get_param("bol_inquiry_sync.client_secret")

        if not client_id or not client_secret:
            return None

        headers = {
            "Content-Type": "application/x-www-form-urlencoded"
        }
        data = {
            "client_id": client_id,
            "client_secret": client_secret,
            "grant_type": "client_credentials"
        }

        try:
            response = requests.post("https://login.bol.com/token", headers=headers, data=data, timeout=30)
            response.raise_for_status()
            result = response.json()
            access_token = result.get("access_token")

            if access_token:
                self.env['ir.config_parameter'].sudo().set_param("bol_inquiry_sync.access_token", access_token)
                return access_token

        except Exception as e:
            _logger = tools.logging.getLogger(__name__)
            _logger.error("Fout bij vernieuwen bol.com access token: %s", str(e))

        return None

    def _get_bol_access_token(self):
        token = self.env['ir.config_parameter'].sudo().get_param("bol_inquiry_sync.access_token")
        if not token:
            token = self._refresh_bol_access_token()
        return token
