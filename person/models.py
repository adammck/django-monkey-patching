#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4


from django.db import models


class Person(models.Model):
    """
        A human being. This class is intended to be extended by other apps, to
        add the fields and functionality needed for the current project. See
        the "gender" and "dob" apps in this project for an example.

          # create a sample person
          >>> adam = Person.objects.create(
          ...   first_name="Adam",
          ...   last_name="Mckaig"
          ... )

          # return their full names
          >>> adam.full_name
          'Adam Mckaig'
    """

    first_name = models.CharField("First Name", max_length=30)
    last_name  = models.CharField("Last Name", max_length=30)

    @property
    def full_name(self):
        return (self.first_name + " " + self.last_name).strip()
