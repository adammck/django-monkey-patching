#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4


from django.db import models


def monkey_patch(parent):
    """
    Adds fields, methods, and properties to a an existing Django model
    by monkey-patching it. But don't freak out. It attempts to prevent
    the extension from breaking the parent by enforcing the following:

    * All of the fields defined in the extension class must be nullable,
      to ensure that the parent class can be instantiated without them.

    * The fields, methods, and properties of the extension class may
      only be _added_ to the parent class. Existing attributes may not
      be touched. (Overwriting existing methods, especially those of
      built-in objects, is not cool.)

    Caveats:

    * Because the extension class is not Django model, just a regular
      class, fields are not inherited, but methods and properties are.
    """

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
        raise_attr_conflicts(parent, ext)

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


def raise_attr_conflicts(dest, source):
    """
    Raise AttributeError if any of the non-magic attributes of *source*
    are already used by *dest*. This should be called before monkey-
    patching *source* into *dest*, to check that the existing behavior
    of *source* won't be changed.
    """

    dest_attrs = non_magic_attrs(dest)
    for attr_name in non_magic_attrs(source):
        if attr_name in dest_attrs:

            raise AttributeError(
                "Attribute '%s.%s' is already defined by '%s'." %
                (source.__name__, attr_name, dest.__name__))

    return True


def non_magic_attrs(obj):
    """
    Return the non-magic attributes of *obj*.

    >>> non_magic_attrs(object)
    []

    >>> class OldExample():
    ...     _a = True
    ...     b = None

    >>> non_magic_attrs(OldExample)
    ['_a', 'b']

    >>> class NewExample(object):
    ...     _c = None
    ...     d = False

    >>> non_magic_attrs(NewExample)
    ['_c', 'd']
    """

    return [x for x in dir(obj) if not is_magic(x)]


def is_magic(name):
    """
    Return True if *name* looks like a __magic__ attribute.

    >>> is_magic("alpha")
    False

    >>> is_magic("__beta__")
    True

    >>> is_magic("_gamma")
    False

    >>> is_magic("_")
    False
    """

    return name.startswith("__") and\
           name.endswith("__") and\
           len(name) >= 5
