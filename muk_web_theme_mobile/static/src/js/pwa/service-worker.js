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

importScripts('https://www.gstatic.com/firebasejs/6.2.4/firebase-app.js');
importScripts('https://www.gstatic.com/firebasejs/6.2.4/firebase-messaging.js');

importScripts('/firebase-config.js');

var staticCacheName = 'site-static-v1';
var dynamicCacheName = 'site-dynamic-v1';

var staticAssets = [
  '/fallback.html'
];

if (firebaseConfig.messagingSenderId) {
	firebase.initializeApp(firebaseConfig);
	firebase.messaging();
}

var openStaticCache = function() {
	return caches.open(staticCacheName);
};

var initiateStaticCache = function() {
	return openStaticCache().then(function(cache) {
		cache.addAll(staticAssets);
	})
};

var clearOutdatedCaches = function() {
	return caches.keys().then(function(keys) {
		var promises = keys.filter(function(key) {
			return key !== staticCacheName && 
				key !== dynamicCacheName;
		}).map(function(key) {
			caches.delete(key)
		});
		return Promise.all(promises);
	});
};

var fetchRequest = function(request) {
	return fetch(request).then(function (response) {
		return response;
	}).catch(function() {
		return caches.match('/fallback.html')
	});
};

self.addEventListener('install', function(ev) {
	ev.waitUntil(initiateStaticCache());
});

self.addEventListener('activate', function(ev) {
	ev.waitUntil(clearOutdatedCaches());
});

self.addEventListener('fetch', function(ev) {
	ev.respondWith(fetchRequest(ev.request));
});
