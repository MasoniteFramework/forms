
from masonite.provider import ServiceProvider

from .form_builder import FormBuilder


class FormsProvider(ServiceProvider):

    wsgi = False

    def register(self):
        pass

    def boot(self, ViewClass):
        self.app.bind('Form', FormBuilder(self.app))

        ViewClass.share({
            'Form': self.app.make('Form')
        })
