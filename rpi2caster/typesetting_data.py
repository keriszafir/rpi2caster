# -*- coding: utf-8 -*-
"""Operations on ribbon and scheme objects: creating, editing and deleting. """
from contextlib import suppress
# Some functions raise custom exceptions
from . import exceptions as e
# Default user data directory
from .defaults import USER_DATA_DIR
# Constants for rpi2caster
from .constants import ASSIGNMENT_SYMBOLS
# User interface, database backend
from .rpi2caster import UI, Abort
from rpi2caster.database import Base, Database, Column, Text
from sqlalchemy.schema import ForeignKey
DB = Database()


class Ribbon(Base):
    """Ribbon objects - no matter whether files or database entries.

    A ribbon has the following attributes:
    description, customer - strings
    diecase_id (diecase is selected automatically on casting, so user can e.g.
                view the layout or know which wedge to use)
    contents - series of Monotype codes

    Methods:
    choose_ribbon - choose ribbon automatically or manually,
        first try to get a ribbon with ribbon_id, and if that fails
        ask and select ribbon manually from database, and if that fails
        ask and load ribbon from file
    read_from_file - select a file, parse the metadata, set the attributes
    export_to_file - store the metadata and contents in text file
    store_in_db - store the metadata and contents in db
    set_[description, customer, diecase_id] - set parameters manually"""
    __tablename__ = 'ribbons'
    ribbon_id = Column('ribbon_id', Text, primary_key=True,
                       default='New Ribbon')
    description = Column('description', Text, default='')
    customer = Column('customer', Text, default='')
    diecase_id = Column('diecase_id', Text,
                        ForeignKey('matrix_cases.diecase_id'))
    wedge_name = Column('wedge', Text, default='', nullable=False)
    contents = Column('contents', Text, default='', nullable=False)

    def __init__(self, parameters=None):
        self.update(parameters)

    def __iter__(self):
        return iter(self.contents)

    def __next__(self):
        yield from self.contents

    def __repr__(self):
        return self.ribbon_id or ''

    def __bool__(self):
        return bool(self.contents)

    @property
    def parameters(self):
        """Gets a list of parameters"""
        return [(self.ribbon_id, 'Ribbon ID'),
                (self.description, 'Description'),
                (self.customer, 'Customer'),
                (self.diecase_id, 'Matrix case ID'),
                (self.wedge_name, 'Wedge')]

    def display_contents(self):
        """Displays the ribbon's contents, line after line"""
        UI.display('Ribbon contents preview:\n')
        contents_generator = (line for line in self.contents if line)
        try:
            while True:
                UI.display(contents_generator.__next__())
        except StopIteration:
            # End of generator
            UI.pause('Finished', UI.MSG_MENU)
        except (EOFError, KeyboardInterrupt):
            # Press ctrl-C to abort displaying long ribbons
            UI.pause('Aborted', UI.MSG_MENU)

    def update(self, source=None):
        """Updates the object attributes with a dictionary"""
        # Allow to use this method to initialize a new empty ribbon
        if not source:
            source = {}
        try:
            UI.display('Processing ribbon data...', min_verbosity=2)
            self.ribbon_id = source.get('ribbon_id', '')
            self.description = source.get('description', '')
            self.customer = source.get('customer', '')
            self.diecase_id = source.get('diecase_id', '')
            self.wedge_name = source.get('wedge_name', '')
            self.contents = source.get('contents', [])
        except AttributeError:
            UI.display('ERROR: Cannot process ribbon data', min_verbosity=2)
            UI.display(source, min_verbosity=2)

    def store_in_db(self):
        """Stores the ribbon in database"""
        UI.display_parameters({'Ribbon data': self.parameters})
        # Ask for confirmation
        try:
            DB.session.add(self)
            UI.pause('Ribbon added successfully.')
            return True
        except (e.DatabaseQueryError, e.NoMatchingData):
            UI.pause('Cannot store ribbon in database!')
            return False

    def delete_from_db(self):
        """Deletes a ribbon from database."""
        if UI.confirm('Are you sure?', default=False):
            DB.session.delete(self)
            UI.display('Ribbon deleted successfully.')

    def import_from_file(self, ribbon_file):
        """Imports ribbon from file, parses parameters, sets attributes"""
        def get_value(line, symbol):
            """Helper function - strips whitespace and symbols"""
            # Split the line on an assignment symbol, get the second part,
            # strip any whitespace or multipled symbols
            return line.split(symbol, 1)[-1].strip(symbol).strip()

        try:
            # Try to open that and get only the lines containing non-whitespace
            with ribbon_file:
                raw_data = (line.strip() for line in ribbon_file.readlines())
                ribbon = [line for line in raw_data if line]
        except AttributeError:
            return False
        # What to look for
        keywords = ['diecase', 'description', 'desc', 'diecase_id', 'customer',
                    'wedge', 'stopbar']
        targets = ['diecase_id', 'description', 'description', 'diecase_id',
                   'customer', 'wedge_name', 'wedge_name']
        parameters = dict(zip(keywords, targets))
        # Metadata (anything found), contents (the rest)
        metadata = {}
        contents = []
        # Look for parameters line per line, get parameter value
        # If parameters exhausted, append the line to contents
        for line in ribbon:
            for keyword, target in parameters.items():
                if line.startswith(keyword):
                    for sym in ASSIGNMENT_SYMBOLS:
                        if sym in line:
                            # Data found
                            metadata[target] = get_value(line, sym)
                            break
                    break
            else:
                contents.append(line)
        # We need to add contents too
        metadata['contents'] = contents
        # Update the attributes with what we found
        self.update(metadata)
        return True

    def export_to_file(self):
        """Exports the ribbon to a text file"""
        UI.display_parameters({'Ribbon data': self.parameters})
        # Choose file, write metadata, write contents
        filename = '%s/%s.rib' % (USER_DATA_DIR, self.ribbon_id)
        with suppress(Abort), UI.export_file(filename) as ribbon_file:
            ribbon_file.write('description: ' + self.description)
            ribbon_file.write('customer: ' + self.customer)
            ribbon_file.write('diecase: ' + self.diecase_id)
            ribbon_file.write('wedge: ' + self.wedge_name)
            for line in self.contents:
                ribbon_file.write(line)

    def import_from_db(self, ribbon_id):
        """Import a ribbon with a given ribbon ID from database"""
        try:
            UI.display('Getting ribbon ID=%s from database...' % ribbon_id,
                       min_verbosity=3)
            result = DB.get_ribbon(ribbon_id)
            self.update(result)
            return True
        except (e.DatabaseQueryError, e.NoMatchingData):
            UI.display('ERROR: Cannot find ribbon!', min_verbosity=2)
            return False

    def choose_from_db(self):
        """Choosea ribbon from database"""
        prompt = 'Number of a ribbon? (0 for a new one, leave blank to exit): '
        while True:
            try:
                # Manual choice if function was called without arguments
                data = list_ribbons()
                choice = UI.enter(prompt, exception=Abort, datatype=int)
                ribbon_id = data[choice]
                # Inform the caller if import was successful or not
                return self.import_from_db(ribbon_id)
            except KeyError:
                UI.pause('Ribbon number is incorrect. Choose again.')
            except (e.DatabaseQueryError, e.NoMatchingData):
                UI.display('WARNING: Cannot find any ribbon data!',
                           min_verbosity=2)
                return False
            except Abort:
                return False


class RibbonMixin(object):
    """Mixin for ribbon-related operations"""
    @property
    def ribbon(self):
        """Ribbon for the casting session"""
        return self.__dict__.get('_ribbon') or Ribbon()

    @ribbon.setter
    def ribbon(self, ribbon):
        """Ribbon setter"""
        self.__dict__['_ribbon'] = ribbon or Ribbon()

    @ribbon.setter
    def ribbon_file(self, ribbon_file):
        """Use a ribbon file"""
        self.ribbon.import_from_file(ribbon_file)

    @ribbon.setter
    def ribbon_id(self, ribbon_id):
        """Use a ribbon with a given ID"""
        self.ribbon.import_from_db(ribbon_id)

    def choose_ribbon(self):
        """Chooses a ribbon from database or file"""
        def from_db():
            """Choose a ribbon from database"""
            prompt = 'Number of a ribbon? (0 for a new one, blank to abort): '
            while True:
                try:
                    # Manual choice if function was called without arguments
                    data = list_ribbons()
                    choice = UI.enter(prompt, exception=Abort, datatype=int)
                    ribbon_id = data[choice]
                    # Inform the caller if import was successful or not
                    return self.import_from_db(ribbon_id)
                except KeyError:
                    UI.pause('Ribbon number is incorrect. Choose again.')
                except (e.DatabaseQueryError, e.NoMatchingData):
                    UI.display('WARNING: Cannot find any ribbon data!',
                               min_verbosity=2)
                    return False
                except Abort:
                    return False

        def from_file():
            """Choose a ribbon from file"""
            # Open the file manually if calling the method without arguments
            try:
                ribbon_file = UI.import_file()
                self.ribbon.import_from_file(ribbon_file)
            except Abort:
                return False
        self.ribbon.choose_from_db() or self.ribbon.import_from_file()


def list_ribbons():
    """Lists all ribbons in the database."""
    data = DB.get_all_ribbons()
    results = {}
    UI.display('\n' +
               'No.'.ljust(5) +
               'Ribbon name'.ljust(30) +
               'Description'.ljust(30) +
               'Customer'.ljust(30) +
               'Diecase'.ljust(30) +
               'Wedge'.ljust(30) +
               '\n\n0 - start a new empty ribbon\n')
    for index, ribbon in enumerate(data, start=1):
        # Collect ribbon parameters
        row = [str(index).ljust(5)]
        # Add ribbon name, description, diecase ID
        row.extend([field.ljust(30) for field in ribbon[:-1]])
        # Display it all
        UI.display(''.join(row))
        # Add number and ID to the result that will be returned
        results[index] = ribbon[0]
    UI.display('\n\n')
    # Now we can return the number - ribbon ID pairs
    return results
