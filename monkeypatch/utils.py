#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4


from django.db import models


def monkey_patch(parent, extension):
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




    The parent class, which will be extended, is just a regular Django
    model. Monkey-patching it is guaranteed not to change its behavior,
    by refusing to apply unless a few conditions are met.

    >>> class Human(models.Model):
    ...     first = models.CharField(max_length=100)
    ...     last  = models.CharField(max_length=100)


    The extension class is a regular new-style class. To avoid circular
    inheritance (and very confusing semantics), this cannot be a Django
    model. Otherwise, the usual inheritance rules apply on both ends.

    >>> class HumanBeardExtension(object):
    ...     has_beard = models.BooleanField(
    ...         null=True, blank=True)
    ...
    ...     @property
    ...     def is_manly(self):
    ...         return self.has_beard is True


    These type constraints are enforced. A TypeError is raised if the
    parent **isn't** a Django model, or the extension **is**.

    >>> class ExampleClass(object):
    ...     pass

    >>> class ExampleModel(models.Model):
    ...     pass

    >>> monkey_patch(ExampleClass, HumanBeardExtension)
    Traceback (most recent call last):
        ...
    TypeError: Class 'ExampleClass' is not a Django model.


    >>> monkey_patch(Human, ExampleModel)
    Traceback (most recent call last):
        ...
    TypeError: Extension class 'ExampleModel' cannot be a Django model.


    If the monkey-patch is successful (ie, no exception is raised), the
    extension class is added to the ancestors of the parent, making its
    methods and properties available.

    >>> Human.__bases__ # doctest: +ELLIPSIS
    (<class 'django...Model'>,)

    >>> monkey_patch(Human, HumanBeardExtension)
    True

    >>> Human.__bases__ # doctest: +ELLIPSIS
    (<class 'django...Model'>, <class '...HumanBeardExtension'>)

    >>> h = Human()
    >>> h.is_manly
    False

    >>> h.has_beard = True
    >>> h.is_manly
    True


    Any Django fields defined in the extension class are copied and
    added to the parent, since those have their own special inheritance.
    (See: http://docs.djangoproject.com/en/dev/topics/db/models/#id5)

    >>> sorted(fields(Human).keys())
    ['first', 'has_beard', 'last']


    >>> class HumanLongNameExtension(object):
    ...     first = models.CharField(max_length=200)

    >>> monkey_patch(Human, HumanLongNameExtension)
    Traceback (most recent call last):
        ...
    AttributeError: Attribute(s) 'first' are already used by 'Human'.
    """

    sanity_check(parent, extension)
    apply_patch(parent, extension)
    return True


def decorator(parent):
    def wrapper(extension):
        return monkey_patch(
            parent, extension)

    return wrapper


def sanity_check(dest, source):
    """
    Returns True if it's (probably) sane to monkey-patch *source* into
    *dest*. It's not an exact science, but the rules are:

    Sorry, RTFS.
    """

    if not issubclass(dest, models.Model):
        raise TypeError(
            "Class '%s' is not a Django model." %
            (dest.__name__))

    if issubclass(source, models.Model):
        raise TypeError(
            "Extension class '%s' cannot be a Django model." %
            (source.__name__))

    confl = conflicts(dest, source)
    if confl:

        flat_conflicts = ", ".join(
            map(repr, confl))

        raise AttributeError(
            "Attribute(s) %s are already used by '%s'." %
            (flat_conflicts, dest.__name__))


def apply_patch(dest, source):
    """
    """

    dest.__bases__ += (source, )

    for name, f in fields(source).items():

        # extension fields can't be NOT NULL, because that would
        # break existing code that isn't aware of the new field(s).
        if not f.null:
            raise TypeError(
                "Field '%s.%s' must be nullable." %
                (source.__name__, name))

        dest.add_to_class(name, f)


def fields(obj):
    """
    Return a dict of the Django fields contained by *obj*, excluding
    those created automatically (eg. primary keys, foreign keys to
    superclasses).

    >>> class Human(models.Model):
    ...     first = models.CharField(max_length=100)
    ...     last  = models.CharField(max_length=100)

    >>> f = fields(Human)
    >>> sorted(f.keys())
    ['first', 'last']

    Model inheritance works as expected.

    >>> class Man(Human):
    ...    beard = models.BooleanField()

    >>> m = Man()
    >>> f = fields(m)
    >>> sorted(f.keys())
    ['beard', 'first', 'last']

    If *obj* is not a Django model, its attributes (and those of its
    ancestors) are searched for subclasses of django.db.models.Field.

    >>> class Alpha(object):
    ...    a = models.IntegerField()
    ...    b = models.IntegerField()

    >>> f = fields(Alpha)
    >>> sorted(f.keys())
    ['a', 'b']

    >>> class Beta(Alpha):
    ...    c = models.BooleanField()

    # FAIL
    #>>> f = fields(Beta)
    #>>> sorted(f.keys())
    #['a', 'b', 'c']
    """

    if hasattr(obj, "_meta"):
        fields = [
            (f.attname, f)
            for f in obj._meta.fields
            if f.auto_created is False]

    else:
        fields = [
            (name, f)
            for name, f in obj.__dict__.items()
            if isinstance(f, models.Field) ]

    return dict(fields)


def conflicts(dest, source):
    """
    Return a set containing the intersection of all non-magic attribute
    names or Django fields between classes *dest* and *source*. If there
    are no common attributes, an empty set is returned.

    >>> class A: a = 1
    >>> class B: b = 2

    >>> class AB:
    ...     def a(self): pass
    ...     def b(self): pass

    >>> conflicts(A, B)
    set([])

    >>> conflicts(A, AB)
    set(['a'])

    >>> conflicts(AB, AB)
    set(['a', 'b'])

    Since Django fields are stashed away in \_meta, those are explicitly
    checked also, to ensure that those don't clash with attributes (or
    other fields) once the class is instantiated.

    >>> class C(models.Model):
    ...     c = models.IntegerField()

    >>> class BC(object):
    ...     b = models.CharField()
    ...     c = True

    >>> conflicts(A, C)
    set([])

    >>> conflicts(AB, BC)
    set(['b'])
    """

    d, s = map(
        lambda obj: set.union(       # the union of...
            set(fields(obj).keys()), # * django field names
            non_magic_attrs(obj)),   # * attribute names
        [dest, source])

    return set.intersection(d, s)


def non_magic_attrs(obj):
    """
    Return a set containing the non-magic attributes of *obj*.

    >>> class Example(object):
    ...     __aaa__ = "MAGIC!"
    ...
    ...     def _b(self):
    ...         pass
    ...
    ...     @property
    ...     def c(self):
    ...         pass
    ...
    ...     d = True
    ...     e = None

    >>> example = Example()
    >>> example.f = "FFF"

    >>> sorted(non_magic_attrs(example))
    ['_b', 'c', 'd', 'e', 'f']

    But watch out for Python's wacky "Private name mangling"!
    http://docs.python.org/reference/expressions.html#index-906

    >>> class Mangled(object):
    ...    __private = None

    >>> non_magic_attrs(Mangled)
    set(['_Mangled__private'])
    """

    return set([
        attr_name
        for attr_name in dir(obj)
        if not is_magic(attr_name) ])


def is_magic(name):
    """
    Return True if *name* looks like a __magic__ attribute.

    >>> is_magic("alpha")
    False

    >>> is_magic("__beta__")
    True

    >>> is_magic("_gamma")
    False

    >>> is_magic("__delta")
    False

    >>> is_magic("_")
    False
    """

    return name.startswith("__") and\
           name.endswith("__") and\
           len(name) >= 5
