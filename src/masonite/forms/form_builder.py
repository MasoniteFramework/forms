
import json
from markupsafe import Markup, escape, escape_silent

from .exceptions import MethodNotAllowed

# TODO: Implement select, checkbox, radio, reset, image, color


class FormBuilder:
    """
    FormBuilder is the class used for building and facilitating form
    interactions.
    """

    ALLOWED_METHODS = ('GET', 'POST', 'PUT', 'PATCH', 'DELETE')
    SPOOFED_METHODS = ('PUT', 'PATCH', 'DELETE')
    SKIP_VALUE_TYPES = ('file', 'password', 'checkbox', 'radio')

    def __init__(self, Container):
        self.container = Container
        self.request = self.container.make('Request')
        self.csrf = self.container.make('Csrf')

        # For the life of me, I could not get loading a session in the provider
        # to work. Probably because the session manger is not loaded in register.
        self.session = None

        # Reset Required
        self._labels = []
        self._model = False
        self._errors = {}

    def _compile_attributes(self, atts):
        """ compiles python values into html attributes """
        atts = ['{}="{}"'.format(name, value) for name, value in atts.items()]
        return ' '.join(atts)

    def open(self, method='GET', url=False, **kwargs):
        """Open up a new HTML form."""
        attributes = {}

        # Retrieve form errors
        self.session = self.container.make('Session')
        if self.container.make('Session').has('errors'):
            try:
                self._errors = json.loads(self.session.get('errors'))
            except ValueError:
                pass

        method = method.upper()
        if method not in self.ALLOWED_METHODS:
            raise MethodNotAllowed("{} is not a valid form method.".format(method))

        attributes['method'] = method if method not in self.SPOOFED_METHODS else "POST"

        if not url:
            attributes['action'] = escape(self.request.path)
        else:
            attributes['action'] = url

        attributes['accept-charset'] = "UTF-8"

        for name, value in kwargs.items():
            attributes[name] = escape(value)

        out = Markup("<form {}>".format(self._compile_attributes(attributes)))
        out = out + self.hidden('__token', value=self.csrf.generate_csrf_token())

        if method in self.SPOOFED_METHODS:
            out = out + self.hidden('__method', value=method)

        return out

    def model(self, model, method="GET", url=None, **kwargs):
        """Creates a new model based on the form builder."""
        self._model = model
        return self.open(method, url, **kwargs)

    def close(self):
        """Closes the current form."""
        self._labels = []
        self._model = False
        self._errors = {}

        return Markup('</form>')

    def report_errors(self, Session, errors):
        """
        This method is intended to be used in controllers. It reports validation
        errors back to the form on the front end.
        """
        for field, value in self.request.all(internal_variables=False).items():
            Session.flash(field, str(value))
        Session.flash('errors', json.dumps(errors))

    def errors(self, name):
        """
        Returns a list of errors for the given input name. If there are no
        errors, we will return None.
        """
        return self._errors.get(name)

    def label(self, name, value=None, escape_html=True, **kwargs):
        """ Renders an html label """
        self._labels.append(name)

        atts = self._compile_attributes(kwargs)

        value = self._format_label(name, value)

        if escape_html:
            value = escape(value)

        return Markup('<label for="{}" {}>{}</label>'.format(name, atts, value))

    def _format_label(self, name, value):
        if value is not None:
            return value

        return name.replace('_', ' ').title()

    def input(self, type, name, value=None, **kwargs):
        """ Renders a generic html input """
        if "name" not in kwargs and name is not None:
            kwargs['name'] = name

        id = self._get_id_attribute(name, kwargs)

        if id is not None:
            kwargs['id'] = id

        if type not in self.SKIP_VALUE_TYPES:
            kwargs['value'] = escape_silent(self._get_value_attribute(name, value))

        kwargs.update({
            'type': type,
        })

        return Markup('<input {} />'.format(self._compile_attributes(kwargs)))

    def text(self, name, value=None, **kwargs):
        """ Renders a text html input """
        return self.input('text', name, value, **kwargs)

    def password(self, name, **kwargs):
        """ Renders a password html input """
        return self.input('password', name, value=None, **kwargs)

    def hidden(self, name, value=None, **kwargs):
        """ Renders a hidden html input """
        return self.input('hidden', name, value=value, **kwargs)

    def search(self, name, value=None, **kwargs):
        """ Renders a search html input """
        return self.input('search', name, value=value, **kwargs)

    def email(self, name, value=None, **kwargs):
        """ Renders a email html input """
        return self.input('email', name, value=value, **kwargs)

    def tel(self, name, value=None, **kwargs):
        """ Renders a tel html input """
        return self.input('tel', name, value=value, **kwargs)

    def number(self, name, value=None, **kwargs):
        """ Renders a number html input """
        return self.input('number', name, value=value, **kwargs)

    def date(self, name, value=None, **kwargs):
        """ Renders a date html input """
        return self.input('date', name, value=value, **kwargs)

    def datetime(self, name, value=None, **kwargs):
        """ Renders a datetime html input """
        return self.input('datetime', name, value=value, **kwargs)

    def datetime_local(self, name, value=None, **kwargs):
        """ Renders a datetime_local html input """
        return self.input('datetime-local', name, value=value, **kwargs)

    def time(self, name, value=None, **kwargs):
        """ Renders a time html input """
        return self.input('time', name, value=value, **kwargs)

    def url(self, name, value=None, **kwargs):
        """ Renders a url html input """
        return self.input('url', name, value=value, **kwargs)

    def file(self, name, **kwargs):
        """ Renders a file html input """
        return self.input('file', name, value=None, **kwargs)

    def textarea(self, name, value, **kwargs):
        """ Renders an html textarea """
        if 'name' not in kwargs:
            kwargs['name'] = name

        kwargs = self._get_text_area_size(kwargs)

        kwargs['id'] = self._get_id_attribute(name, kwargs)

        value = self._get_value_attribute(name, value)

        if 'size' in kwargs:
            del kwargs['size']

        return Markup('<textarea {}>%s</textarea>'.format(self._compile_attributes(kwargs))) % value

    def submit(self, value=None, **kwargs):
        """ Renders a submit html input """
        return self.input('submit', None, value=value, **kwargs)

    def button(self, value=None, **kwargs):
        """ Renders an html button """
        if 'type' not in kwargs:
            kwargs['type'] = 'button'

        return Markup('<button {}>%s</button>'.format(self._compile_attributes(kwargs))) % value

    def _get_text_area_size(self, kwargs):
        if 'size' in kwargs:
            return self._set_quick_text_area_size(kwargs)

        cols = kwargs.get('cols', 50)
        rows = kwargs.get('rows', 10)

        kwargs.update({
            'cols': cols,
            'rows': rows
        })

        return kwargs

    def _set_quick_text_area_size(self, kwargs):
        parts = kwargs['size'].split('x')

        kwargs.update({
            'cols': parts[0],
            'rows': parts[1],
        })

        return kwargs

    def _get_id_attribute(self, name, attributes):
        if 'id' in attributes:
            return attributes['id']
        return name

    def _get_value_attribute(self, name, value=None):
        if name is None:
            return value

        old = self.old(name)

        if old and not name == '__method':
            return old

        request_value = self.request.input(name)
        if request_value and not name == 'request_method':
            return request_value

        if value is not None:
            return value

        if self._model:
            return self._get_model_value_attribute(name)

        return None

    def _get_model_value_attribute(self, name):
        if hasattr(self._model, 'get_form_value') and callable(self._model.get_form_value):
            return self._model.get_form_value(name)

        if hasattr(self._model, name):
            return getattr(self._model, name)

        return None

    def old(self, name):
        if self.session is not None and self.session.has(name):
            return self.session.get(name)
        return False
