# Copyright 2004 Roman Yakovenko.
# Distributed under the Boost Software License, Version 1.0. (See
# accompanying file LICENSE_1_0.txt or copy at
# http://www.boost.org/LICENSE_1_0.txt)

import sys, os, os.path
from distutils import sysconfig
from distutils.core import setup
from distutils.cmd import Command

try:
    sys.path.append("../pygccxml_dev")
    import pygccxml
    pygccxml_available = True
except ImportError:
    pygccxml_available = False
    

def generate_doc():
    """Generate the epydoc reference manual.
    """
    if not pygccxml_available:
        print "Please install pygccxml before generating the docs."
        sys.exit()
        
    print "Generating epydoc files..."
    options = [ '--output="%s"'%os.path.join('docs', 'apidocs'),
                '--docformat=epytext',
                '--url=http://www.language-binding.net',
                '--name=pyplusplus',
#                '--verbose',
                'pyplusplus']
    cmd_line = "epydoc " + ' '.join( options )
    print cmd_line
    os.system(cmd_line)
    

class doc_cmd(Command):
    """This is a new distutils command 'doc' to build the epydoc manual.
    """

    description = 'build the API reference using epydoc'
    user_options = [('no-doc', None, "don't run epydoc")]
    boolean_options = ['no-doc']

    def initialize_options (self):
        self.no_doc = 0
        
    def finalize_options (self):
        pass
    
    def run(self):
        if self.no_doc:
            return
        generate_doc()


# Generate the doc when a source distribution is created
if sys.argv[-1]=="sdist":
    generate_doc()


setup( name = "pyplusplus",
       version = "0.7.1",
       description="pyplusplus is a framework of components for creating C++ code generator for boost.python library",
       author="Roman Yakovenko",
       author_email="roman.yakovenko@gmail.com",
       url='http://www.language-binding.net/pyplusplus/pyplusplus.html',
       scripts = ["scripts/pyplusplus_gui",
                  "scripts/pyplusplus_gui.pyw"],
       packages=[ 'pyplusplus',
                  'pyplusplus.gui',
                  'pyplusplus.file_writers',
                  'pyplusplus.code_creators',
                  'pyplusplus.module_creator',
                  'pyplusplus.code_repository',
                  'pyplusplus.decl_wrappers',
                  'pyplusplus.module_builder',
                  'pyplusplus.utils',
                  'pyplusplus._logging_'],
       cmdclass = {"doc" : doc_cmd}
)
