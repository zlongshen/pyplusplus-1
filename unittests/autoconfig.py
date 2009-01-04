#! /usr/bin/python
# Copyright 2004-2008 Roman Yakovenko.
# Distributed under the Boost Software License, Version 1.0. (See
# accompanying file LICENSE_1_0.txt or copy at
# http://www.boost.org/LICENSE_1_0.txt)

import os
import sys
import unittest
import subprocess


this_module_dir_path = os.path.abspath ( os.path.dirname( sys.modules[__name__].__file__) )

data_directory = os.path.join( this_module_dir_path, 'data' )
build_directory = os.path.join( this_module_dir_path, 'temp' )
build_dir = build_directory

sys.path.append( os.path.dirname( this_module_dir_path ) )

from environment import scons, boost, python, gccxml, indexing_suite

import pygccxml

compiler = pygccxml.utils.native_compiler.get_gccxml_compiler()
print 'GCCXML configured to simulate compiler ', compiler
gccxml_version = '__GCCXML_09__'
class cxx_parsers_cfg:
    keywd = { 'working_directory' : data_directory
              , 'define_symbols' : [ gccxml_version ]
              , 'compiler' : compiler
              , 'gccxml_path': gccxml.executable }

    if 'win' in sys.platform:
        keywd['define_symbols'].append( '__PYGCCXML_%s__' % compiler.upper() )
        if 'msvc9' == compiler:
            keywd['define_symbols'].append( '_HAS_TR1=0' )

    gccxml = pygccxml.parser.gccxml_configuration_t( **keywd )



class scons_config:
    libs = []
    libpath = [ python.libs ] + boost.libs
    cpppath = [ boost.include, python.include, indexing_suite.include ]
    include_dirs = cpppath + [data_directory]

    @staticmethod
    def create_sconstruct():
        msvc_compiler = ''
        if 'linux' not in sys.platform:
            msvc_compiler = str( pygccxml.utils.native_compiler.get_version()[1] )
        else:
            scons_config.libs.append( 'boost_python' )
        code = [
              "import sys"
            , "env = Environment()"
            , "if 'linux' not in sys.platform:"
            , "    env['MSVS'] = {'VERSION': '%s'}" % msvc_compiler
            , "    env['MSVS_VERSION'] = '%s'" % msvc_compiler
            , "    Tool('msvc')(env)"
            , "t = env.SharedLibrary( target=r'%(target)s'"
            , "    , source=[ %(sources)s ]"
            , "    , LIBS=[ %s ]" % ','.join( [ 'r"%s"' % lib for lib in scons_config.libs ] )
            , "    , LIBPATH=[ %s ]" % ','.join( [ 'r"%s"' % path for path in scons_config.libpath ] )
            , "    , CPPPATH=[ %s ]" % ','.join( [ 'r"%s"' % path for path in scons_config.include_dirs] )
            , "    , CCFLAGS=[ %s ]" % ','.join( [ 'r"%s"' % flag for flag in scons.ccflags ] )
            , "    , SHLIBPREFIX=''"
            , "    , SHLIBSUFFIX='%s'" % scons.suffix #explicit better then implicit
            , ")" ]
            #~ , "if 'linux' not in sys.platform:"
            #~ , "    env.AddPostAction(t, 'mt.exe -nologo -manifest %(target)s.pyd.manifest -outputresource:%(target)s.pyd;2'  )" ]
        return os.linesep.join( code )

    @staticmethod
    def compile( cmd ) :
        print '\n', cmd
        process = subprocess.Popen( args=cmd
                                    , shell=True
                                    , stdin=subprocess.PIPE
                                    , stdout=subprocess.PIPE
                                    , stderr=subprocess.STDOUT
                                    , cwd=this_module_dir_path )
        process.stdin.close()

        while process.poll() is None:
            line = process.stdout.readline()
            print line.rstrip()
        for line in process.stdout.readlines():
            print line.rstrip()
        if process.returncode:
            raise RuntimeError( "unable to compile extension. error: %s" % scons_msg )


#I need this in order to allow Python to load just compiled modules
sys.path.append( build_dir )

os.chdir( build_dir )

if sys.platform == 'win32':
    PATH = os.environ.get( 'PATH', '' )
    PATH=PATH + ';' + ';'.join( scons_config.libpath )
    os.environ['PATH'] = PATH
