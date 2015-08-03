"""
typesetter - program for generating the code sequence fed to
a Monotype composition caster or type&rule caster.

This program reads an input file (UTF-8 text file) or allows to enter
a string, then parses it, auto-hyphenates (with TeX hyphenation algorithm),
calculates justification figures and outputs the combinations of Monotype
signals, one by one, to the file or database. These sequences are to be read
and parsed by the casting program, which sends the signals to the machine.
"""
# User interface
from rpi2caster.global_settings import USER_INTERFACE as ui
# Exceptions module
from rpi2caster import exceptions
# Wedge and database operations
from rpi2caster import typesetting_functions as backend
# HTML/XML parser:
try:
    from bs4 import BeautifulSoup
except ImportError:
    raise exceptions.MissingDependency('BeautifulSoup 4 not installed!')


# Start with an un-configured typesetting job
def main_menu(job=backend.Typesetter()):
    """main_menu

    Calls ui.menu() with options, a header and a footer.
    Also defines some subroutines for appending information.
    """

    # Declare local functions for menu options:
    def start_new_session():
        """Starts new typesetting session"""
        job.session_setup()

    def choose_input_filename():
        """Chooses a source text from file"""
        input_file = ui.enter_input_filename()
        with open(input_file) as text_file:
            job.text_source = job.parse_and_generate(text_file)

    def options_constructor():
        """Dynamically build menu based on conditions"""
        options = [('Exit program', exceptions.exit_program),
                   ('Start new typesetting session', start_new_session),
                   ('Load a text file', choose_input_filename)]
        if job.diecase_layout:
            options.append(('Display diecase layout', job.show_layout))
        if job.diecase_layout and job.text_source:
            options.append(('Compose the text', job.compose))
        return options

    # Commands: {option_name : function}
    hdr = ('rpi2caster - CAT (Computer-Aided Typecasting) '
           'for Monotype Composition or Type and Rule casters. \n\n'
           'This program reads a ribbon (input file) and casts the type '
           'on a Composition Caster, \n'
           'or punches a paper tape with a pneumatic perforator.' +
           '\n\nMain Menu:')
    while True:
        # Call the function and return to menu.
        try:
            ui.menu(options_constructor(), header=hdr)()
        except exceptions.ReturnToMenu:
            pass
        except (KeyboardInterrupt, exceptions.ExitProgram):
            ui.exit_program()
