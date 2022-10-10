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

odoo.define('muk_web_theme_mobile.dialogs', function (require) {
"use strict";

var core = require('web.core');
var config = require("web.config");

var Dialog = require('web.Dialog');

var _t = core._t;
var QWeb = core.qweb;

var Many2OneSearchDialog = Dialog.extend({
    template: 'muk_web_theme_mobile.FieldMany2OneDialog',
    events: _.extend({}, Dialog.prototype.events, {
    	"keydown .mk_one2many_input": "_onSearchKeydown",
    	"click .mk_one2many_entry": "_onEntryClick",
    	"click .mk_one2many_quick_create": "_onQuickCreateClick",
    }),
    init: function (parent, options) {
    	var search_result = options && options.result;
        this.has_value = !!(options && options.value);
        this.current_term = options && options.term;
        this.quick_create = this._get_quick_create(search_result);
        this.search_entries = _.filter(search_result, function(entry) {
        	return entry.label && entry.value && entry.id; 
        });
        this._super(parent, $.extend(true, options || {},  {
        	buttons: this._get_buttons(search_result),
        }));
        this.getSearchResult = options && options.on_search;
        this.deleteCurrentValue = options && options.on_delete;
        this.triggerAction = options && options.on_action;
        this.triggerSelect = options && options.on_select;
        this._onSearchKeydown = _.debounce(this._onSearchKeydown, 250);
    },
    _get_quick_create: function(search_result) {
    	return _.find(search_result, function(entry) {
			var template = _t('Create "<strong>%s</strong>"');
			var text = $('<span />').text(this.current_term).html();
			return entry.label == _.str.sprintf(template, text);
		}.bind(this));
    },
    _get_buttons: function(search_result) {
        var actions = _.filter(search_result, function(entry) {
        	if (this.quick_create && this.quick_create.action_id) {
        		return entry.action_id !== this.quick_create.action_id &&
        			entry.action_id;
        	}
        	return entry.action_id; 
        }.bind(this));
        var buttons = _.map(actions, function(action) {
        	return {
                text: action.label.replace("...", ""),
                click: this._onButtonAction.bind(this, action),
                classes: 'btn-primary',
                close: true,
            }
        }.bind(this));
        if (this.has_value) {
        	buttons = buttons.concat([{
                icon: 'fa-trash-o',
                click: this._onDeleteClick.bind(this),
                classes: 'btn-danger mk_one2many_delete',
                close: true,
            }]);
        }
        return buttons;
    },
    _onButtonAction: function(action, event) {
    	return this.triggerAction(action.action_id);
    },
    _onDeleteClick: function(event) {
    	return this.deleteCurrentValue();
    },
    _onEntryClick: function(event) {
    	var $entry = $(event.currentTarget);
    	$.when(this.triggerSelect({
    		display_name: $entry.data('name'),
    		id: $entry.data('id'),
    	})).always(this.close.bind(this));
    },
    _onQuickCreateClick: function(event) {
    	var $entry = $(event.currentTarget);
    	var def = this.triggerAction($entry.data('id'));
    	$.when(def).always(this.close.bind(this));
    },
    _onSearchKeydown: function(event) {
    	this.current_term = this.$('.mk_one2many_input').val();
    	this.getSearchResult(this.current_term).then(function(result) {
    		this.quick_create = this._get_quick_create(result);
    		this.set_buttons(this._get_buttons(result));
    		this.search_entries = _.filter(result, function(entry) {
            	return entry.label && entry.value && entry.id; 
            });
    		var template = 'muk_web_theme_mobile.FieldMany2OneEntries';
    		var $content = $(QWeb.render(template, {
        		search_entries: this.search_entries,
        		quick_create: this.quick_create,
        	}).trim());
    		this.$('.mk_one2many_result').replaceWith($content);
    	}.bind(this));
    }
});

return {
	Many2OneSearchDialog: Many2OneSearchDialog,
};

});