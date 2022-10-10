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
import jinja2

from odoo import http, SUPERUSER_ID, api
from odoo.modules import registry, get_resource_path
from odoo.tools.mimetypes import guess_mimetype
from odoo.tools import config
from odoo.http import request

from odoo.addons.muk_utils.tools.utils import safe_execute

path = os.path.join(os.path.dirname(__file__), '..', 'static/src/html')

jinja_loader = jinja2.FileSystemLoader(os.path.realpath(path))
jinja_env = jinja2.Environment(loader=jinja_loader, autoescape=True)
jinja_env.filters["json"] = json.dumps

class ProgressiveWebApp(http.Controller):
    
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
    
    def _get_mobile_manifest_data(self, dbname, uid, company=None):
        try:
            fields = ", ".join([
                "c.mobile_screen_name",
                "c.mobile_menu_name",
                "c.mobile_background_color",
                "c.mobile_theme_color",
            ])
            dbreg = registry.Registry(dbname)
            with dbreg.cursor() as cr:
                if company:
                    cr.execute("""
                        SELECT {0}, c.write_date
                        FROM res_company c
                        WHERE id = %s        
                    """.format(fields), (company,))
                else:
                    cr.execute("""
                        SELECT {0}, c.write_date
                        FROM res_users u
                        LEFT JOIN res_company c
                        ON c.id = u.company_id
                        WHERE u.id = %s
                    """.format(fields), (uid,))
                return cr.dictfetchone()
        except Exception:
            return {}
    
    def _get_mobile_sender_id(self, dbname):
        try:
            dbreg = registry.Registry(dbname)
            with dbreg.cursor() as cr:
                env = api.Environment(cr, SUPERUSER_ID, {})
                return env['ir.config_parameter'].sudo().get_param(
                    'muk_web_theme_mobile.cm_sender_id'
                )
        except Exception:
            return None
    
    @http.route('/manifest.json', type='http', auth="none")
    def mobile_manifest(self, dbname=None, **kw):
        company = self._get_company_id(kw.get('company', False))
        dbname, uid = self._get_database_and_user(dbname)
        if dbname:
            manifest_data = self._get_mobile_manifest_data(dbname, uid, company)
            manifest = {
                "name": manifest_data.get('mobile_screen_name', 'MuK'),
                "short_name" : manifest_data.get('mobile_menu_name', 'MuK'),
                "theme_color" : manifest_data.get('mobile_theme_color', '#212529'),
                "background_color": manifest_data.get('mobile_background_color', '#243742'),
                "gcm_sender_id": "103953800507",
                "display": "standalone",
                "start_url": "/web",
                "scope" : "/", 
                "icons": [{
                    "src": "/mobile-192x192.png",
                    "sizes": "192x192",
                    "type": "image/png"
                }, {
                    "src": "/mobile-512x512.png",
                    "sizes": "512x512",
                    "type": "image/png"
                }],
            }
            response = http.send_file(
                io.BytesIO(json.dumps(manifest).encode()), 
                filename='manifest.json', mimetype='application/json',
                mtime=manifest_data.get('write_date', None),
            )
        else:
            file = get_resource_path('muk_web_theme_mobile', 'static', 'src', 'manifest.json')
            response = http.send_file(file, filename='manifest.json', mimetype='application/json')
        return response
    
    @http.route('/service-worker.js', type='http', auth="none")
    def mobile_service_worker(self, **kw):
        file = get_resource_path('muk_web_theme_mobile', 'static', 'src', 'js', 'pwa', 'service-worker.js')
        return http.send_file(file, filename='service-worker.js', mimetype='application/javascript')
    
    @http.route('/firebase-config.js', type='http', auth="none")
    def mobile_firebase_config(self, dbname=None, **kw):
        dbname, uid = self._get_database_and_user(dbname)
        sender_id = self._get_mobile_sender_id(dbname)
        content = """
            var firebaseConfig = {
                messagingSenderId: '%(sender_id)s',
            };
        """ % {'sender_id': sender_id}
        return http.send_file(
            io.BytesIO(content.encode()),
            filename='firebase-config.js', 
            mimetype='application/javascript'
        )
    
    @http.route('/fallback.html', type='http', auth="none")
    def mobile_offline_fallback(self, **kw):
        return jinja_env.get_template("fallback.html").render({})