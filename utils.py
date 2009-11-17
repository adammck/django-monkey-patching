#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4


from django.db import models


def monkey_patch(parent):
    def wrapper(ext):

        if not issubclass(parent, models.Model):
            raise TypeError(
                "Class '%s' is not a subclass of django.db.models.Model" %
                (parent.__name__))

        # add fields from the extension into the model
        for name, field in ext.__dict__.items():
            if isinstance(field, models.Field):

                # extension fields can't be NOT NULL, because that would
                # break the code that isn't aware of the extension
                if not field.null:
                    raise TypeError(
                        "Field '%s.%s' must be nullable." %
                        (ext.__name__, field.name))

                parent.add_to_class(name, field)

        # monkeypatch the extension class into the superclasses of the
        # parent, so all of the methods in the extension are inherited
        parent.__bases__ += (ext,)
        return ext

    return wrapper
