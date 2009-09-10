#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4


from django.db import models
from person.models import Person


# add a useful property and some useless methods to the Person
# model, by appending this class to it's inheritance chain
class PersonExtensionGender(object):
    """
        Adds a Gender field to the Person model, to track the penis/vagina ratio
        of our humans. This class should be added to the __bases__ attribute of
        Person.

          # create a sample person in the usual way, to
          # ensure that our extension hasn't broken it
          >>> adam = Person.objects.create(
          ...   first_name="Adam",
          ...   last_name="Mckaig"
          ... )

          # check that the gender property was added
          # to this instance, and it defaulted to empty
          # (but not NULL - that would break everything)
          >>> adam.gender
          ''

          # create another sample person, this time with
          # a gender, and check that it was set correctly
          >>> merrick = Person.objects.create(
          ...   first_name="Merrick",
          ...   last_name="Schaefer",
          ...   gender="M"
          ... )
          >>> merrick.gender
          'M'

          # check that our useless extension methods to Person
          # were added, and correctly access the instance attrs
          >>> merrick.is_male()
          True

          >>> merrick.is_female()
          False
    """

    # add the GENDER field to the Person class with a monkey-patch. if
    # we add this field to the PersonExtension class, django ignores it.
    # it doesn't need to be in this scope, but i think it's clearer
    Person.add_to_class(
        "gender",

        models.CharField(
            "Gender",
            max_length=1,
            blank=True,
            choices=(
                ("M", "Male"),
                ("F", "Female")
            )
        )
    )

    def is_male(self):
        return (self.gender == "M")

    def is_female(self):
        return (self.gender == "F")

Person.__bases__ += (PersonExtensionGender,)
