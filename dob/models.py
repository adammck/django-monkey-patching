#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4


from datetime import datetime, timedelta
from django.db import models
from person.models import Person


# add a useful property to the Person model, by
# appending this class to it's inheritance chain
class PersonExtensionDob(object):
    """
        Adds a Data of Birth field to the Person model, to track the age of our
        humans. This class should be added to the __bases__ attribute of Person.

          # create a sample person in the usual way, to
          # ensure that our extension hasn't broken it
          >>> adam = Person.objects.create(
          ...   first_name="Adam",
          ...   last_name="Mckaig"
          ... )

          # check that the date_of_birth
          # property exists in this instance
          >>> hasattr(adam, "date_of_birth")
          True

          # set the date of birth (one week ago)
          >>> dob = datetime.today() - timedelta(7)
          >>> adam.date_of_birth = dob

          # check that the extensions methods to Person
          # are available by fetching the age in days
          >>> adam.days_old
          7

          # create another person, passing their date
          # of birth to the constructor (two weeks ago)
          >>> dob = datetime.today() - timedelta(14)
          >>> evan = Person.objects.create(
          ...   first_name="Evan",
          ...   last_name="Wheeler",
          ...   date_of_birth=dob
          ... )

          >>> evan.days_old
          14
    """

    # add the DATE OF BIRTH field to the Person class with a monkey-patch.
    # if we add this field to the PersonExtension class, django ignores it.
    # it doesn't need to be in this scope, but i think it's clearer
    Person.add_to_class(
        "date_of_birth",

        models.DateField(
            "Date of Birth",
            blank=True,
            null=True
        )
    )

    @property
    def days_old(self):
        """Returns the age, in days, of this Person."""

        if self.date_of_birth:
            delta = (datetime.today() - self.date_of_birth)
            return delta.days

        else:
            return None

Person.__bases__ += (PersonExtensionDob,)
