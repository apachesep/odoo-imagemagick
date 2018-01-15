# -*- coding: utf-8 -*-
##############################################################################
#
# Odoo, Open Source Management Solution, third party addon
# Copyright (C) 2018- Vertel AB (<http://vertel.se>).
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

import openerp
from openerp import http
from openerp.addons.web.http import request
from openerp.addons.website_memcached import memcached

from openerp.addons.website.website_imagemagic import website_imagemagic

import logging
_logger = logging.getLogger(__name__)

    
class CachedImageMagick(website_imagemagic):
    
    #~ @http.route(['/imagemagick/<model("ir.attachment"):image>/id/<model("image.recipe"):recipe>',
                 #~ '/imagemagick/<model("ir.attachment"):image>/ref/<string:recipe_id>'], type='http', auth="public", website=True)
    @memcached@route(flush_type='imagemagick',binary=True)
    def view_attachment(self, image=None, recipe=None, recipe_ref=None, **post):
        return super(CachedWebsite, self).view_attachment(image, recipe, recipe_ref, **post)
  

    #~ @http.route(['/imageurl/<string:url>/id/<model("image.recipe"):recipe>','/imageurl/<string:url>/ref/<string:recipe>'], type='http', auth="public", website=True)
    @memcached@route(flush_type='imagemagick',binary=True,send_file=True)
    def view_url(self, url=None, recipe=None, recipe_ref=None, **post):
        return super(CachedWebsite, self).view_url(url, recipe, recipe_ref, **post)


    #~ @http.route([
        #~ '/imagefield/<model>/<field>/<id>/ref/<recipe_ref>',
        #~ '/imagefield/<model>/<field>/<id>/id/<model("image.recipe"):recipe>',
        #~ ], type='http', auth="public", website=True, multilang=False)
    @memcached@route(flush_type='imagemagick',binary=True,send_file=True)
    def website_image(self, model, id, field, recipe=None,recipe_ref=None):
        return super(CachedWebsite, self).website_image(model, id, field, recipe,recipe_ref)

    #~ @http.route([
        #~ '/imagefieldurl/<model>/<field>/<id>/ref/<recipe_ref>',
        #~ '/imagefieldurl/<model>/<field>/<id>/id/<model("image.recipe"):recipe>',
        #~ ], type='http', auth="public", website=True, multilang=False)
    @memcached@route(flush_type='imagemagick',binary=True,send_file=True)
    def website_url(self, model, id, field, recipe=None,recipe_ref=None):
        return super(CachedWebsite, self).website_url(model, id, field, recipe,recipe_ref)


    #~ @http.route([
        #~ '/website/imagemagick/<model>/<field>/<id>/<model("image.recipe"):recipe>',
        #~ ], type='http', auth="public", website=True, multilang=False)
    @memcached@route(flush_type='imagemagick',binary=True)
    def website_imagemagick(self, model, field, id, recipe=None):
        return super(CachedWebsite, self).website_imagemagick(model, field, id, recipe)