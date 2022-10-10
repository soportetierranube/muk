###################################################################################
#
#    Copyright (c) 2017-2019 MuK IT GmbH.
#
#    This file is part of MuK Backend Theme Mobile 
#    (see https://mukit.at).
#
#    MuK Proprietary License v1.0
#
#    This software and associated files (the "Software") may only be used 
#    (executed, modified, executed after modifications) if you have
#    purchased a valid license from MuK IT GmbH.
#
#    The above permissions are granted for a single database per purchased 
#    license. Furthermore, with a valid license it is permitted to use the
#    software on other databases as long as the usage is limited to a testing
#    or development environment.
#
#    You may develop modules based on the Software or that use the Software
#    as a library (typically by depending on it, importing it and using its
#    resources), but without copying any source code or material from the
#    Software. You may distribute those modules under the license of your
#    choice, provided that this license is compatible with the terms of the 
#    MuK Proprietary License (For example: LGPL, MIT, or proprietary licenses
#    similar to this one).
#
#    It is forbidden to publish, distribute, sublicense, or sell copies of
#    the Software or modified copies of the Software.
#
#    The above copyright notice and this permission notice must be included
#    in all copies or substantial portions of the Software.
#
#    THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
#    OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#    FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
#    THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#    LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
#    FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
#    DEALINGS IN THE SOFTWARE.
#
###################################################################################

import re
import json
import requests
import html2text

from odoo import models, fields, api

FCM_SEND_URL = "https://fcm.googleapis.com/fcm/send"

CM_CLICK_URL_TEMPLATE = "%s/web#action=%d&active_id=mailbox_inbox&menu_id=%d"
CM_ICON_URL_TEMPLATE = "%s/mobile-192x192.png"

class MailMessage(models.Model):
    
    _inherit = 'mail.message'

    #@api.multi
    def _notify_recipients(self, rdata, record, msg_vals, **kwargs):
        super(MailMessage, self)._notify_recipients(rdata, record, msg_vals, **kwargs)
        chat_ids = [data['id'] for data in rdata['channels'] if data['type'] == 'chat']
        partner_ids = [data['id'] for data in rdata['partners']]
        if chat_ids or partner_ids:
            channel_partner_ids = []
            message = self.sudo()
            if chat_ids:
                channel_model = self.env['mail.channel'].sudo()
                channel_partner_ids = channel_model.search([
                    ('id', 'in', chat_ids),
                ]).mapped("channel_partner_ids").ids
            if msg_vals.get('message_type', message.message_type)  == 'comment':
                complete_partner_ids = (set(partner_ids) | set(channel_partner_ids))
                complete_partner_ids -= set(message.author_id.ids)
                if complete_partner_ids:    
                    params = self.env['ir.config_parameter'].sudo()
                    subscription_model = self.env['muk_web_theme_mobile.subscription'].sudo()
                    subscriptions = subscription_model.search([('partner', 'in', list(complete_partner_ids))])
                    server_key = params.get_param('muk_web_theme_mobile.cm_server_key', False)
                    registration_ids = subscriptions.mapped('subscription')
                    if registration_ids and server_key:
                        self._send_cloud_message(message, registration_ids, server_key)
    
    #@api.model
    def _prepare_cloud_message(self, message, tokens):
        params = self.env['ir.config_parameter'].sudo()
        menu = self.env.ref('mail.menu_root_discuss').id
        action = self.env.ref('mail.action_discuss').id
        base_url = params.get_param('web.base.url')
        notification = {
            "icon": CM_ICON_URL_TEMPLATE % base_url,
            "click_action": CM_CLICK_URL_TEMPLATE % (
                base_url, action, menu
            ),
        }
        payload = {
            "notification": notification,
            "registration_ids": tokens
        }
        if message.model == 'mail.channel':
            channel = message.channel_ids.filtered(
                lambda rec: rec.id == message.res_id
            )
            if channel.channel_type == 'chat':
                notification['title'] = message.author_id.name
        if 'title' not in notification or not notification['title']:
            title = message.record_name or message.subject
            notification['title'] = title
        payload_size = len(str(payload).encode())
        payload_body_size = 4000 - payload_size
        if payload_body_size > 0:
            html = re.sub(r'<\/?a.*?>', r'<a>', message.body)
            body = html2text.html2text(html)[:payload_body_size]
            notification['body'] = body
        return payload
    
    #@api.model
    def _send_cloud_message(self, message, tokens, server_key):
        payload = self._prepare_cloud_message(message, tokens)
        requests.post(FCM_SEND_URL, headers={
            'Content-Type':'application/json',
            'Authorization': "key=%s" % server_key,
        }, data=json.dumps(payload))
