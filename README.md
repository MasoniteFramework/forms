Masonite Forms
==============

Masonite Forms is an very lightweight form management package built for the
Masonite framework.

Currently, this package is in alpha at best. It is not even close to production
ready. We need to add support for selects, checkboxes, radios, resets, images,
and colors. Additionally, there are no tests. So we'll have to write those
before this is ready to go.

For those of you who want to try it out, take a look at the source below.

Step 1: Create a model

```python
''' A Thing Database Model '''
from config.database import Model

class Thing(Model):
    __table__ = 'things'
    __fillable__ = ['first_name', 'last_name', 'email', 'password']

```

Step 2: Create a controller to do stuff with your model

```python

from validator import Required, Not, Blank, validate

from app.Thing import Thing


class TestFormsController:

    def edit(self, Request, Container):
        return view('edit', {'instance': Thing(first_name='Abram', last_name='Isola')})

    def update(self, Request, Session, Form):
        ok, errors = self.validate_input(Request.all())
        if not ok:

            # Form.report_errors, is a convenience function which flashes the
            # data and errors back to the form in the front end.
            Form.report_errors(Session, errors)

            return Request.redirect_to('test_forms')

        # Do something meaningful with the data

        return Request.redirect_to('licenses')

    def validate_input(self, data):
        rules = {
            'first_name': [Required, Not(Blank())],
            'last_name': [Required, Not(Blank())],
            'email': [Required, Not(Blank())],
            'password': [Required, Not(Blank())],
        }

        return validate(rules, data)
```

Step 3: Create your form inside of the html data. Notice our call to
`Form.model`. We use this method because we are passing a model instance on
which to base the form fields. Should we want to start without a model, we
should use `Form.open`.

```html

<!DOCTYPE html>
<html>
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Testing Forms</title>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/bulma/0.7.1/css/bulma.min.css">
    <script defer src="https://use.fontawesome.com/releases/v5.0.7/js/all.js"></script>
  </head>
  <body>
    <section class="section">
      <div class="container">
        <div class="column is-4 is-offset-4">


          <h1 class="title">Testing Forms</h1>
          <!-- Open a form, based on a database record. We also define the request method, the action, and any other attributes. -->
          {{ Form.model(instance, method="PUT", url='/test/update', class="form", enctype="multipart/form-data") }}

            <div class="field">
              <div class="control">
                <!-- Create a label for the text input first_name -->
                {{ Form.label("first_name", class="label") }}

                <!-- Create the text input first_name -->
                {{ Form.text("first_name", class="input", placeholder="Abram", autofocus="") }}

                <!-- If the form fails to validate, then we'll just report the errors here. -->
                {% if Form.errors('first_name') %}
                  {% for e in Form.errors('first_name') %}
                    <p class="help is-danger">{{ e }}</p>
                  {% endfor %}
                {% endif %}
              </div>
            </div>

            <div class="field">
              <div class="control">
                {{ Form.label("last_name", class="label") }}
                {{ Form.text("last_name", class="input", placeholder="Isola") }}
                {% if Form.errors('last_name') %}
                  {% for e in Form.errors('last_name') %}
                    <p class="help is-danger">{{ e }}</p>
                  {% endfor %}
                {% endif %}
              </div>
            </div>

            <div class="field">
              <div class="control">
                {{ Form.label("email", class="label") }}
                {{ Form.email("email", class="input", placeholder="abram.isola@example.com") }}
                {% if Form.errors('email') %}
                  {% for e in Form.errors('email') %}
                    <p class="help is-danger">{{ e }}</p>
                  {% endfor %}
                {% endif %}
              </div>
            </div>

            <div class="field">
              <div class="control">
                {{ Form.label("password", class="label") }}
                {{ Form.password("password", class="input", placeholder="Super Secret") }}
                {% if Form.errors('password') %}
                  {% for e in Form.errors('password') %}
                    <p class="help is-danger">{{ e }}</p>
                  {% endfor %}
                {% endif %}
              </div>
            </div>

            <div class="field">
              <div class="control">
                {{ Form.label("resume", class="label") }}
                {{ Form.file("resume", class="resume") }}
                {% if Form.errors('resume') %}
                  {% for e in Form.errors('resume') %}
                    <p class="help is-danger">{{ e }}</p>
                  {% endfor %}
                {% endif %}
              </div>
            </div>

            <div class="field">
              <div class="control">
                {{ Form.button('Submit', type='submit', class='button') }}
              </div>
            </div>

          <!-- REMEMBER to close your form when you are done with it. -->
          {{ Form.close() }}

        </div>
      </div>
    </section>
  </body>
</html>

```
