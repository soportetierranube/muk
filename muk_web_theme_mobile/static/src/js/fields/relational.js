/**********************************************************************************
*
*    Copyright (c) 2017-2019 MuK IT GmbH.
*
*    This file is part of MuK Backend Theme Mobile 
*    (see https://mukit.at).
*
*    MuK Proprietary License v1.0
*
*    This software and associated files (the "Software") may only be used 
*    (executed, modified, executed after modifications) if you have
*    purchased a valid license from MuK IT GmbH.
*
*    The above permissions are granted for a single database per purchased 
*    license. Furthermore, with a valid license it is permitted to use the
*    software on other databases as long as the usage is limited to a testing
*    or development environment.
*
*    You may develop modules based on the Software or that use the Software
*    as a library (typically by depending on it, importing it and using its
*    resources), but without copying any source code or material from the
*    Software. You may distribute those modules under the license of your
*    choice, provided that this license is compatible with the terms of the 
*    MuK Proprietary License (For example: LGPL, MIT, or proprietary licenses
*    similar to this one).
*
*    It is forbidden to publish, distribute, sublicense, or sell copies of
*    the Software or modified copies of the Software.
*
*    The above copyright notice and this permission notice must be included
*    in all copies or substantial portions of the Software.
*
*    THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
*    OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
*    FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
*    THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
*    LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
*    FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
*    DEALINGS IN THE SOFTWARE.
*
**********************************************************************************/

odoo.define('muk_web_theme_mobile.relational_fields', function (require) {
"use strict";

var core = require('web.core');
var config = require("web.config");
var relational_fields = require('web.relational_fields');
var dialogs = require('muk_web_theme_mobile.dialogs');

var _t = core._t;
var QWeb = core.qweb;

if (!config.device.isMobile) {
    return;
}

relational_fields.FieldMany2One.include({
    _bindAutoComplete: function () {
    	return;
    },
    _onInputClick: function () {
    	return this._openMobileDialog('');
    },
    _prepareSearch: function (result) {
    	this._dialog_actions = {};
    	_.each(result, function (res, idx) {
            if (!res.hasOwnProperty('id')) {
            	this._dialog_actions[idx] = res.action;
                result[idx].action_id = idx;
            }
        }.bind(this));
    	return result;
    },
    _openMobileDialog: function (term) {
        this._search(term).then(function (result) {
        	this._prepareSearch(result);
            var options = {
                term: term,
                result: result,
                value: this.value,
                title: _t("Select: ") + this.string, 
                on_select: function (record) {
                	this.reinitialize(record);
                }.bind(this),
                on_action: function (action) {
                	this._dialog_actions[action]();
                }.bind(this),
                on_delete: function () {
                	this.reinitialize(false);
                }.bind(this),
                on_search: function (term) {
                	return this._search(term).then(function (result) {
                		return this._prepareSearch(result);
                	}.bind(this));
                }.bind(this),
                fullscreen: true,
            }
            new dialogs.Many2OneSearchDialog(this, options).open();
        }.bind(this));
    },
});

});