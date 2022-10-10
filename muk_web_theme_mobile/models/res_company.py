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

from odoo import models, fields, api
from odoo.tools import image

MOBILE_SIZES = ['512', '192', '180', '167', '152', '144']

class ResCompany(models.Model):
    
    _inherit = 'res.company'
    
    #----------------------------------------------------------
    # Database
    #----------------------------------------------------------
    
    mobile_screen_name = fields.Char(
        string="Mobile Screen Name",
        default="System")
    
    mobile_menu_name = fields.Char(
        string="Mobile Menu Icon Name",
        default="System")
    
    mobile_background_color = fields.Char(
        string="Mobile Background Color",
        default="#243742")
    
    mobile_theme_color = fields.Char(
        string="Mobile Theme Color",
        default="#212529")
    
    mobile_icon_144 = fields.Binary(
        string="Mobile Icon 144x144",
        attachment=False)
    
    mobile_icon_152 = fields.Binary(
        string="Mobile Icon 152x152",
        attachment=False)
    
    mobile_icon_167 = fields.Binary(
        string="Mobile Icon 167x167",
        attachment=False)
    
    mobile_icon_180 = fields.Binary(
        string="Mobile Icon 180x180",
        attachment=False)
    
    mobile_icon_192 = fields.Binary(
        string="Mobile Icon 192x192",
        attachment=False)
    
    mobile_icon_512 = fields.Binary(
        string="Mobile Icon 512x512",
        attachment=False)
    
    #----------------------------------------------------------
    # Helper
    #----------------------------------------------------------
    
    def _get_resized_mobile_icons(self, base64_source):
        if isinstance(base64_source, str):
            base64_source = base64_source.encode('ascii')
        avoid_if_small = False
        return {
            'mobile_icon_512': image.image_resize_image(base64_source, (512, 512), avoid_if_small=avoid_if_small),
            'mobile_icon_192': image.image_resize_image(base64_source, (192, 192), avoid_if_small=avoid_if_small),
            'mobile_icon_180': image.image_resize_image(base64_source, (180, 180), avoid_if_small=avoid_if_small),
            'mobile_icon_167': image.image_resize_image(base64_source, (167, 167), avoid_if_small=avoid_if_small),
            'mobile_icon_152': image.image_resize_image(base64_source, (152, 152), avoid_if_small=avoid_if_small),
            'mobile_icon_144': image.image_resize_image(base64_source, (144, 144), avoid_if_small=avoid_if_small),
        }
        
    def _resize_mobile_icons(self, vals):
        if vals.get('mobile_icon_512'):
            vals.update(self._get_resized_mobile_icons(vals['mobile_icon_512']))
        elif vals.get('mobile_icon_192'):
            vals.update(self._get_resized_mobile_icons(vals['mobile_icon_192']))    
        elif vals.get('mobile_icon_180'):
            vals.update(self._get_resized_mobile_icons(vals['mobile_icon_180']))   
        elif vals.get('mobile_icon_167'):
            vals.update(self._get_resized_mobile_icons(vals['mobile_icon_167']))   
        elif vals.get('mobile_icon_152'):
            vals.update(self._get_resized_mobile_icons(vals['mobile_icon_152']))   
        elif vals.get('mobile_icon_144'):
            vals.update(self._get_resized_mobile_icons(vals['mobile_icon_144']))   
        elif any('mobile_icon_%s' % size in vals for size in MOBILE_SIZES):
            for size in MOBILE_SIZES:
                vals['mobile_icon_%s' % size] = False
                
    #----------------------------------------------------------
    # Create, Update, Delete
    #----------------------------------------------------------
    
    #@api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            self._resize_mobile_icons(vals)
        return super(ResCompany, self).create(vals_list)
        
    #@api.multi
    def write(self, vals):
        self._resize_mobile_icons(vals)
        return super(ResCompany, self).write(vals)
            
    
