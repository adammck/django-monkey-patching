#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4


from django.db import models


def monkey_patch(parent):
    if not issubclass(parent, models.Model):
        raise TypeError(
            "Class '%s' is not a Django model." %
            (parent.__name__))

    def wrapper(ext):

        # if the extension class is a django model, it will create a
        # circular inheretance chain, which will blow up with a type
        # error later when it's added to parent.__bases__. catch this
        # mistake early, to inform the author what they're doing wrong.
        if issubclass(ext, models.Model):
            raise TypeError(
                "Extension class '%s' cannot be a Django model." %
                (ext.__name__))

        # check that none of the non __magic__ attributes of the
        # extension are already defined in the parent. this wouldn't
        # cause an error, but would cause rather confusion behavior.
        parent_dir = dir(parent)
        for attr_name in dir(ext):
            if not is_magic(attr_name) and\
               attr_name in parent_dir:

                raise AttributeError(
                    "Attribute '%s.%s' is already defined." %
                    (parent.__name__, attr_name))

        # add fields from the extension into the model.
        for name, field in ext.__dict__.items():
            if isinstance(field, models.Field):

                # extension fields can't be NOT NULL, because that would
                # break the code that isn't aware of the extension.
                if not field.null:
                    raise TypeError(
                        "Field '%s.%s' must be nullable." %
                        (ext.__name__, field.name))

                parent.add_to_class(name, field)

        # monkeypatch the extension class into the superclasses of the
        # parent, so all of the methods in the extension are inherited.
        parent.__bases__ += (ext,)
        return ext

    return wrapper


def is_magic(name):
    """
    Return true if *name* looks like a __magic__ attribute.
    """

    return name.startswith("__") and\
           name.endswith("__") and\
           len(name) >= 5
