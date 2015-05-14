#!/usr/bin/python
import rpi2caster

session = rpi2caster.Session(database=rpi2caster.Database('database/monotype.db'),
                             job=rpi2caster.Typesetting())
