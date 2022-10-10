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

import io
import os
import json
import base64
import mimetypes
import functools

from odoo import http, SUPERUSER_ID
from odoo.modules import registry, get_resource_path
from odoo.tools.mimetypes import guess_mimetype
from odoo.tools import config
from odoo.http import request

from odoo.addons.web.controllers.main import Binary
from odoo.addons.muk_utils.tools.utils import safe_execute

class Binary(Binary):
    
    def _get_company_id(self, company):
        return safe_execute(False, int, company) if company else False
    
    def _get_database_and_user(self, dbname):
        uid = None
        dbname = None
        if request.session.db:
            dbname = request.session.db
            uid = request.session.uid
        elif dbname is None:
            dbname = http.db_monodb()
        return dbname, uid or SUPERUSER_ID
    
    def _get_mobile_icon_placeholder(self):
        if config.get("default_mobile_icon_folder", False):
            def get_path(filename):
                return os.path.join(config.get("default_company_image_folder"), filename)
            return get_path
        return functools.partial(get_resource_path, 'muk_web_theme_mobile', 'static', 'src', 'img')
    
    def _get_mobile_icon_response(self, dbname, size, default_mimetype='image/png', company=False):
        company = self._get_company_id(company)
        dbname, uid = self._get_database_and_user(dbname)
        placeholder = self._get_mobile_icon_placeholder()
        mobile_icon_name = "mobile_icon_%s" % size
        if not dbname:
            response = http.send_file(
                placeholder("%s.png" % mobile_icon_name)
            )
        else:
            company_data = self._get_company_image_data(
                dbname, uid, mobile_icon_name, company
            )
            if company_data and company_data[0]:
                image_data = base64.b64decode(company_data[0])
                mimetype = guess_mimetype(image_data, default=default_mimetype)
                extension = mimetypes.guess_extension(mimetype)
                response = http.send_file(
                    io.BytesIO(image_data), filename=('icon%s' % extension),
                    mimetype=mimetype, mtime=company_data[1]
                )
            else:
                response = http.send_file(
                    placeholder("%s.png" % mobile_icon_name)
                )
        return response    
    
    @http.route(['/web/binary/mobile/512x512', '/mobile-512x512', '/mobile-512x512.png'], type='http', auth="none")
    def mobile_icon_512(self, dbname=None, **kw):
        return self._get_mobile_icon_response(dbname, 512, self._get_company_id(kw.get('company', False)))
        
    @http.route(['/web/binary/mobile/192x192', '/mobile-192x192', '/mobile-192x192.png'], type='http', auth="none")
    def mobile_icon_192(self, dbname=None, **kw):
        return self._get_mobile_icon_response(dbname, 192, self._get_company_id(kw.get('company', False)))
        
    @http.route(['/web/binary/mobile/180x180', '/mobile-180x180', '/mobile-180x180.png'], type='http', auth="none")
    def mobile_icon_180(self, dbname=None, **kw):
        return self._get_mobile_icon_response(dbname, 180, self._get_company_id(kw.get('company', False)))
        
    @http.route(['/web/binary/mobile/167x167', '/mobile-167x167', '/mobile-167x167.png'], type='http', auth="none")
    def mobile_icon_167(self, dbname=None, **kw):
        return self._get_mobile_icon_response(dbname, 167, self._get_company_id(kw.get('company', False)))
        
    @http.route(['/web/binary/mobile/152x152', '/mobile-152x152', '/mobile-152x152.png'], type='http', auth="none")
    def mobile_icon_152(self, dbname=None, **kw):
        return self._get_mobile_icon_response(dbname, 152, self._get_company_id(kw.get('company', False)))
        
    @http.route(['/web/binary/mobile/144x144', '/mobile-144x144', '/mobile-144x144.png'], type='http', auth="none")
    def mobile_icon_144(self, dbname=None, **kw):
        return self._get_mobile_icon_response(dbname, 144, self._get_company_id(kw.get('company', False)))