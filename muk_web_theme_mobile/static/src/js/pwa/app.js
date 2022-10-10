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

odoo.define('muk_web_theme_mobile.app', function (require) {
"use strict";

var ajax = require('web.ajax');
var session = require("web.session");

if (!('serviceWorker' in navigator)) {
	return;
}

var workerRegistered = navigator.serviceWorker.register(
	'/service-worker.js'
);

if (!session.muk_web_theme_mobile_cm_sender_id) {
	console.warn("No Could Messaging Sender ID set!");
} else {
	firebase.initializeApp({
		messagingSenderId: session.muk_web_theme_mobile_cm_sender_id,
	});

	workerRegistered.then((registration) => {
		firebase.messaging().useServiceWorker(registration);
	});

	if ('Notification' in window) {
		Notification.requestPermission().then(function(permission) {
			if (permission === 'granted') {
				var messaging = firebase.messaging();
				messaging.getToken().then(function(currentToken) {
					ajax.rpc('/web/dataset/call_kw/muk_web_theme_mobile.subscription/register_device', {
				        model: 'muk_web_theme_mobile.subscription',
				        method: 'register_device',
				        args: [currentToken],
				        kwargs: {},
				    });
				});
			}
		});
	}
}

});