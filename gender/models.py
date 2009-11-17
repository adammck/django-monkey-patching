#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4


from django.db import models
from person.models import Person
from monkeypatch import monkey_patch


@monkey_patch(Person)
class PersonExtensionGender(object):
    """
    Extends Person with a 'gender' field and some helper methods. After
    being extended, the Person model continues to work as before:

    >>> evan = Person.objects.create(
    ...   first_name="Evan",
    ...   last_name="Wheeler")

    # hehe. i crack me up
    >>> evan.androgynous
    True


    ...but the extra fields, methods, and proprties are available as if
    Person had inherited them via Django's model inheritance:

    >>> merrick = Person.objects.create(
    ...   first_name="Merrick",
    ...   last_name="Schaefer",
    ...   gender="M")

    >>> merrick.gender
    'M'

    >>> merrick.is_male()
    True

    >>> merrick.androgynous
    False
    """

    gender = models.CharField(max_length=1, null=True, blank=True, choices=
        (("M", "Male"), ("F", "Female")))

    def is_male(self):
        return (self.gender == "M")

    def is_female(self):
        return (self.gender == "F")

    @property
    def androgynous(self):
        return (self.gender is None)
