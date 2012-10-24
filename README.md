django_jqueryglobalize
======================

Re-using Django's internationalization on the client side with javascript using ``Globalize``

Read more about ``Globalize`` at [https://github.com/jquery/globalize](https://github.com/jquery/globalize).

Instead of supplying all languages you want to support to the client side, ``django_jqueryglobalize`` creates the javascript culture info for ``Globalize`` on the fly, based on the currently selected language.

This also makes it possible to harmonize the way Django renders data on the server side with your client side data presentation in an easy fashion.

- Install ``django_jqueryglobalize`` by putting the ``django_jqueryglobalize`` inside your django application
- Add the javascript_catalog extension to the urls:
```python
(r'^globalize/', 'django_globalize.views.javascript_catalog'),
```
- Be sure to include the resources in your html:
```html
<script src="{{STATIC_URL}}js/globalize.js" type="text/javascript"></script>
<script src="/jsi18n_ext" type="text/javascript"></script>
```
