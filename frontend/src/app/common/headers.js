"use strict";
var http_1 = require('@angular/http');
exports.contentHeaders = new http_1.Headers();
exports.contentHeaders.append('Accept', 'application/json');
exports.contentHeaders.append('Content-Type', 'application/json');
exports.contentHeaders.append('Access-Control-Allow-Origin', 'http://localhost');