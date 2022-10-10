# -*- coding: utf-8 -*-
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
"""
Store database-specific configuration parameters
"""

import uuid
import logging

from odoo import api, fields, models
from odoo.tools import config, ormcache

_logger = logging.getLogger(__name__)


class Subscription(models.Model):
    
    _name = 'muk_web_theme_mobile.subscription'
    _description = 'Push Manager Subscriptions'

    #----------------------------------------------------------
    # Database
    #----------------------------------------------------------
    
    name = fields.Char(
        compute='_compute_name',
        string="Name",
        store=True)

    partner = fields.Many2one(
        comodel_name='res.partner',
        string="Partner",
        required=True, 
        index=True)
    
    subscription = fields.Text(
        string="Subscription ID",
        required=True, 
        index=True)


    #----------------------------------------------------------
    # SQL Constraints
    #----------------------------------------------------------
    
    _sql_constraints = [
        ('subscription_unique', 'unique (subscription)', 'Subscription must be unique!')
    ]

    #----------------------------------------------------------
    # Functions
    #----------------------------------------------------------#
    
    #@api.model
    @ormcache('self._uid', 'partner_id')
    def get_subscriptions(self, partner_id):
        return self.search_read([
            ('partner', '=', partner_id)
        ], fields=['subscription'], limit=1)
        
    #@api.model
    def set_subscription(self, partner_id, subscription):
        record = self.search([('subscription', '=', subscription)])
        if record:
            record.write({
                'partner': partner_id
            })
        else:
            self.create({
                'partner': partner_id,
                'subscription': subscription
            })
    
    #@api.model
    def register_device(self, subscription):
        partner_id = self.env.user.partner_id.id
        self.sudo().set_subscription(partner_id, subscription)
        
    #----------------------------------------------------------
    # Read
    #----------------------------------------------------------
    
    @api.depends('partner', 'subscription')
    def _compute_name(self):
        for record in self:
            record.name = "%s - %s" % (record.partner, record.subscription[:10])
    
    #----------------------------------------------------------
    # Update
    #----------------------------------------------------------

    #@api.model_create_multi
    def create(self, vals_list):
        self.clear_caches()
        return super(Subscription, self).create(vals_list)

    #@api.multi
    def write(self, vals):
        self.clear_caches()
        return super(Subscription, self).write(vals)

    #@api.multi
    def unlink(self):
        self.clear_caches()
        return super(Subscription, self).unlink()
