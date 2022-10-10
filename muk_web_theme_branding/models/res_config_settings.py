###################################################################################
#
#    Copyright (c) 2017-2019 MuK IT GmbH.
#
#    This file is part of MuK Backend Theme Branding 
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
import uuid
import base64

from odoo import api, fields, models

FONTS_XML_ID = "muk_web_theme_branding._assets_backend_helpers"
FONTS_SCSS_URL = "/muk_web_theme_branding/static/src/scss/fonts.scss"

VARIABLES_XML_ID = "muk_web_theme_branding._assets_primary_variables"
VARIABLES_SCSS_URL = "/muk_web_theme_branding/static/src/scss/variables.scss"

class ResConfigSettings(models.TransientModel):

    _inherit = 'res.config.settings'

    #----------------------------------------------------------
    # Database
    #----------------------------------------------------------
    
    theme_branding_font_root_size = fields.Float(
        string="Font Root Size")
    
    theme_branding_line_base_height = fields.Float(
        string="Line Base Height")
    
    theme_branding_label_size_factor = fields.Float(
        string="Label Size Factor")
    
    theme_branding_font = fields.Selection(
        selection=[
            ('Roboto', 'Roboto'),
            ('Exo', 'Exo'),
            ('Fira', 'Fira'),
            ('Lato', 'Lato'),
            ('Montserrat', 'Montserrat'),
            ('Noto', 'Noto'),
            ('Poppins', 'Poppins'),
            ('Railway', 'Railway'),
            ('Taviraj', 'Taviraj'),
            ('Trirong', 'Trirong'),
        ],
        string="Font",
        default='Roboto',
        required=True)
    
    #----------------------------------------------------------
    # Helper
    #----------------------------------------------------------
    
    #@api.model
    def _get_font_template_xmlid(self, font):
        return 'muk_web_theme_branding.assets_common_font_%s' % str(font).lower()
    
    #@api.model
    def _get_font_template_record(self, font):
        return self.env.ref(self._get_font_template_xmlid(font))
    
    #@api.model
    def _get_font_template_records(self):
        records = self.env['ir.ui.view']
        fonts = dict(self._fields['theme_branding_font'].selection) 
        templates = filter(lambda k: k not in ['Roboto', 'Noto'], fonts.keys())
        for template in templates:
            records |= self._get_font_template_record(template)       
        return records
    
    #@api.model
    def _get_font_values(self):
        return self.env['muk_utils.scss_editor'].get_values(
            VARIABLES_SCSS_URL, VARIABLES_XML_ID, [
                'o-root-font-size',
                'o-line-height-base',
                'o-label-font-size-factor',
            ]
        )
        
    #@api.model
    def _get_active_font(self):
        return self.env['muk_utils.scss_editor'].get_values(
            FONTS_SCSS_URL, FONTS_XML_ID, ['font-family-sans-serif']
        )['font-family-sans-serif'].split(",")[0].strip("'")
    
    #@api.model
    def _check_font_values(self, fonts, variables):
        for values in variables:
            if fonts[values['name']] != values['value']:
                return True
        return False
    
    def _set_font_values(self):
        variables = [{
            'name': 'o-root-font-size',
            'value': "%.2fpx" %  self.theme_branding_font_root_size or 12
        }, {
            'name': 'o-line-height-base',
            'value': "%.2f" %  self.theme_branding_line_base_height or 1.5
        }, {
            'name': 'o-label-font-size-factor',
            'value': "%.2f" %  self.theme_branding_label_size_factor or 0.8
        }]
        values = self._get_font_values()
        if self._check_font_values(values, variables):
            self.env['muk_utils.scss_editor'].replace_values(
                VARIABLES_SCSS_URL, VARIABLES_XML_ID, variables
            )
        
    def _set_active_font(self):
        active_font = self._get_active_font()
        if active_font != self.theme_branding_font:
            editor = self.env['muk_utils.scss_editor']
            if self.theme_branding_font == 'Roboto':
                editor.reset_values(FONTS_SCSS_URL, FONTS_XML_ID)
            elif self.theme_branding_font == 'Noto':
                editor.replace_values(FONTS_SCSS_URL, FONTS_XML_ID, [{
                    'name': 'font-family-sans-serif',
                    'value': "'Noto'",
                }])
            else:
                editor.replace_values(FONTS_SCSS_URL, FONTS_XML_ID, [{
                    'value': "'%s', 'Noto'" %  self.theme_branding_font,
                    'name': 'font-family-sans-serif',
                }]) 
            template_records = self._get_font_template_records()
            if self.theme_branding_font not in ['Roboto', 'Noto']:
                active_record = self._get_font_template_record(
                    self.theme_branding_font
                )
                template_records = template_records - active_record
                active_record.write({'active': True})
            template_records.write({'active': False})
        
    #----------------------------------------------------------
    # Functions
    #----------------------------------------------------------
    
    #@api.multi 
    def set_values(self):
        res = super(ResConfigSettings, self).set_values()
        self._set_font_values()
        self._set_active_font()
        return res

    #@api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        sizes = self._get_font_values()
        res.update({
            'theme_branding_font_root_size': float(re.search(".+?(?=px)", sizes['o-root-font-size']).group(0)),
            'theme_branding_line_base_height': float(sizes['o-line-height-base']),
            'theme_branding_label_size_factor': float(sizes['o-label-font-size-factor']),
            'theme_branding_font': self._get_active_font(),
        })
        return res