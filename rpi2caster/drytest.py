#!/usr/bin/python
import text_ui
from rpi2caster import Session, set_ui
import simulation
import casting
import database

UI = set_ui([simulation, casting, database])

with Session(job=casting.Casting(),
            db=database.Database('database/monotype.db'),
            caster=simulation.Monotype()) as session:
    pass
