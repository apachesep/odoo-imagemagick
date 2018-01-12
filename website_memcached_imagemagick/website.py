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
    def CachedImageMagick(self, image=None, recipe=None, recipe_ref=None, **post):
        return super(CachedWebsite, self).view_attachment(image, recipe, recipe_ref, **post)




  #~ @http.route('/page/<page:page>', type='http', auth="public", website=True)
    @memcached.route(flush_type='page')
    def page(self, page, **opt):
        return super(CachedWebsite, self).page(page, **opt)
        if recipe_ref:
            recipe = request.env.ref(recipe_ref)
        if recipe:
            return recipe.send_file(http, attachment=image)
        return request.registry['website']._image(
                request.cr, request.uid, 'ir.attachment','%s_%s' % (image.id, hashlib.sha1(image.sudo().write_date or image.sudo().create_date or '').hexdigest()[0:7]),
                'datas', werkzeug.wrappers.Response(),250,250,cache=STATIC_CACHE)

    # this controller will control url: /image/image_url/magic/recipe_id
    @http.route(['/imageurl/<string:url>/id/<model("image.recipe"):recipe>','/imageurl/<string:url>/ref/<string:recipe>'], type='http', auth="public", website=True)
    def view_url(self, url=None, recipe=None, recipe_ref=None, **post):
        if recipe_ref:
            recipe = request.env.ref(recipe_ref) # 'imagemagick.my_recipe'
        return recipe.send_file(http, url=url)


    @http.route([
        '/imagefield/<model>/<field>/<id>/ref/<recipe_ref>',
        '/imagefield/<model>/<field>/<id>/id/<model("image.recipe"):recipe>',
        #~ '/imageobj/<>/ref/<string:recipe>'

        ], type='http', auth="public", website=True, multilang=False)
    def website_image(self, model, id, field, recipe=None,recipe_ref=None):
        if recipe_ref:
            recipe = request.env.ref(recipe_ref) # 'imagemagick.my_recipe'
        #~ recipe.send_file(http,field=field,model=model,id=id.split('_')[0])
        return recipe.sudo().send_file(http,field=field,model=model,id=id)

    @http.route([
        '/imagefieldurl/<model>/<field>/<id>/ref/<recipe_ref>',
        '/imagefieldurl/<model>/<field>/<id>/id/<model("image.recipe"):recipe>',
        ], type='http', auth="public", website=True, multilang=False)
    def website_url(self, model, id, field, recipe=None,recipe_ref=None):
        if recipe_ref:
            recipe = request.env.ref(recipe_ref)
        o = request.env[model].browse(int(id))
        url = getattr(o, field).strip()
        attachment_id = int(url.split('/')[6].split('_')[0])
        return recipe.send_file(http,field='datas',model='ir.attachment',id=attachment_id)

    @http.route([
        '/website/imagemagick/<model>/<field>/<id>/<model("image.recipe"):recipe>',
        ], type='http', auth="public", website=True, multilang=False)
    def website_imagemagick(self, model, field, id, recipe=None):
        try:
            idsha = id.split('_')
            id = idsha[0]
            response = werkzeug.wrappers.Response()
            return request.env['website']._imagemagick(
                model, id, field, recipe, response,
                cache=STATIC_CACHE if len(idsha) > 1 else None)
        except Exception:
            _logger.exception("Cannot render image field %r of record %s[%s] with recipe[%s]",
                             field, model, id, recipe.id)
            response = werkzeug.wrappers.Response()
            return self.placeholder(response)
    """
     class werkzeug.contrib.cache.FileSystemCache(cache_dir, threshold=500, default_timeout=300, mode=384)

    A cache that stores the items on the file system. This cache depends on being the only user of the cache_dir. Make absolutely sure that nobody but this cache stores files there or otherwise the cache will randomly delete files therein.
    Parameters:

        cache_dir – the directory where cache files are stored.
        threshold – the maximum number of items the cache stores before it starts deleting some.
        default_timeout – the default timeout that is used if no timeout is specified on set().
        mode – the file mode wanted for the cache files, default 0600

    """

    def placeholder(self, response):
        return request.env['website']._image_placeholder(response)

class website(models.Model):
    _inherit = 'website'

    #~ def _image_placeholder(self, response):
        #~ """
        #~ Choose placeholder.
        #~ """
        #~ # file_open may return a StringIO. StringIO can be closed but are
        #~ # not context managers in Python 2 though that is fixed in 3
        #~ with contextlib.closing(openerp.tools.misc.file_open(
                #~ os.path.join('web', 'static', 'src', 'img', 'placeholder.png'),
                #~ mode='rb')) as f:
            #~ response.data = f.read()
            #~ return response.make_conditional(request.httprequest)

    @api.model
    def imagemagick_url(self, record, field, recipe, id=None):
        """Returns a local url that points to the image field of a given browse record, run through an imagemagick recipe.
           Record can be a record object, external id or model name (requires id to be given as well).
           Recipe can be a record object, external id, or an id.
        """
        if type(record) is str:
            if id:
                record = self.env[record].browse(id)
            else:
                record = self.env.ref(record).sudo()
        model = record._name
        sudo_record = record.sudo()
        if type(recipe) is str:
            sudo_recipe = self.env.ref(recipe).sudo()
        elif type(recipe) is int:
            sudo_recipe = self.env['image.recipe'].browse(recipe).sudo()
        else:
            sudo_recipe = recipe.sudo()
        id = '%s_%s' % (record.id, hashlib.sha1('%s%s' % (sudo_record.write_date or sudo_record.create_date or '',
            sudo_recipe.write_date or sudo_recipe.create_date or '')).hexdigest())
        return '/website/imagemagick/%s/%s/%s/%s' % (model, field, id, sudo_recipe.id)

    # WIP. Very temporary solution.
    @api.model
    def _imagemagick(self, model, id, field, recipe, response, cache=None):
        """ Fetches the requested field and applies the given imagemagick recipe on it.

        If the record is not found or does not have the requested field,
        returns a placeholder image via :meth:`~._image_placeholder`.

        Sets and checks conditional response parameters:
        * :mailheader:`ETag` is always set (and checked)
        * :mailheader:`Last-Modified is set iif the record has a concurrency
          field (``__last_update``)

        The requested field is assumed to be base64-encoded image data in
        all cases.
        """
        _logger.warn('\n\n\nfoobar')
        user = self.env['res.users'].browse(self._uid)
        o = self.env[model].sudo().browse(int(id))
        if o.check_access_rights('read', raise_exception=False):
            return recipe.sudo().send_file(http,field=field,model=model,id=id)
        if 'website_published' in o.fields_get().keys() and o.website_published == True:
            if user.has_group('base.group_website_publisher') or recipe.website_published == True:
                return recipe.sudo().send_file(http,field=field,model=model,id=id)
        return recipe.send_file(http,field=field,model=model,id=id)

        record = self.env[model].browse(id)
        if not len(record) > 0 and 'website_published' in record._fields:
            record = self.env[model].sudo().search(
                                [('id', '=', id),
                                ('website_published', '=', True)])
        if not len(record) > 0:
            return self._image_placeholder(response)

        concurrency = '__last_update'
        record = record.sudo()
        if hasattr(record, concurrency):
            server_format = openerp.tools.misc.DEFAULT_SERVER_DATETIME_FORMAT
            try:
                response.last_modified = datetime.datetime.strptime(
                    getattr(record, concurrency), server_format + '.%f')
            except ValueError:
                # just in case we have a timestamp without microseconds
                response.last_modified = datetime.datetime.strptime(
                    getattr(record, concurrency), server_format)

        # Field does not exist on model or field set to False
        if not hasattr(record, field) and getattr(record, field) and recipe:
            # FIXME: maybe a field which does not exist should be a 404?
            return self._image_placeholder(response)

        #TODO: Keep format of original image.
        img = recipe.run(Image(blob=getattr(record, field).decode('base64'))).make_blob() #format='jpg')
        response.set_etag(hashlib.sha1(img).hexdigest())
        response.make_conditional(request.httprequest)

        if cache:
            response.cache_control.max_age = cache
            response.expires = int(time.time() + cache)

        # conditional request match
        if response.status_code == 304:
            return response

        data = img.decode('base64')
        image = Image.open(cStringIO.StringIO(data))
        response.mimetype = Image.MIME[image.format]

        filename = '%s_%s.%s' % (model.replace('.', '_'), id, str(image.format).lower())
        response.headers['Content-Disposition'] = 'inline; filename="%s"' % filename

        response.data = data

        return response

