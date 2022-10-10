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

from odoo import api, SUPERUSER_ID

from . import models

#----------------------------------------------------------
# Hooks
#----------------------------------------------------------

FONTS_XML_ID = "muk_web_theme_branding._assets_backend_helpers"
FONTS_SCSS_URL = "/muk_web_theme_branding/static/src/scss/fonts.scss"

VARIABLES_XML_ID = "muk_web_theme_branding._assets_primary_variables"
VARIABLES_SCSS_URL = "/muk_web_theme_branding/static/src/scss/variables.scss"

def _uninstall_reset_changes(cr, registry):
    env = api.Environment(cr, SUPERUSER_ID, {})
    env['muk_utils.scss_editor'].reset_values(FONTS_SCSS_URL, FONTS_XML_ID)
    env['muk_utils.scss_editor'].reset_values(VARIABLES_SCSS_URL, VARIABLES_XML_ID)