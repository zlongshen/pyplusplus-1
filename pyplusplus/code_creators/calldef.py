# Copyright 2004 Roman Yakovenko
# Distributed under the Boost Software License, Version 1.0. (See
# accompanying file LICENSE_1_0.txt or copy at
# http://www.boost.org/LICENSE_1_0.txt)

import os
import algorithm
import code_creator
import calldef_utils
import declaration_based
import registration_based
import class_declaration
from pygccxml import declarations
from pyplusplus import decl_wrappers

#TODO:
#Add to docs:
#public memebr functions - call, override, call base implementation
#protected member functions - call, override
#private - override

class calldef_t( registration_based.registration_based_t
                 , declaration_based.declaration_based_t ):
    def __init__(self, function, wrapper=None ):
        registration_based.registration_based_t.__init__( self )
        declaration_based.declaration_based_t.__init__( self, declaration=function )
        self._wrapper = wrapper
        self._associated_decl_creators = []

    @property
    def associated_decl_creators( self ):
        """ references to declaration code creators. """
        return self._associated_decl_creators

    def _get_wrapper( self ):
        return self._wrapper
    def _set_wrapper( self, new_wrapper ):
        self._wrapper = new_wrapper
    wrapper = property( _get_wrapper, _set_wrapper )

    def def_identifier( self ):
        return algorithm.create_identifier( self, '::boost::python::def' )

    def pure_virtual_identifier( self ):
        return algorithm.create_identifier( self, '::boost::python::pure_virtual' )

    def param_sep(self):
        return os.linesep + self.indent( self.PARAM_SEPARATOR )

    def create_keywords_args(self):
        arg_utils = calldef_utils.argument_utils_t( self.declaration, algorithm.make_id_creator( self ) )
        return arg_utils.keywords_args()

    def create_call_policies( self ):
        if self.declaration.call_policies.is_default():
            return ''
        return self.declaration.call_policies.create( self )
                
    def create_def_code( self ):
        if not self.works_on_instance:
            return '%s.def' % self.parent.class_var_name
        else:
            return 'def'

    def create_doc(self):
        return self.documentation

    def create_function_ref_code( self, use_function_alias=False ):
        raise NotImplementedError()

    def _get_function_type_alias( self ):
        return self.alias + '_function_type'
    function_type_alias = property( _get_function_type_alias )

    def _get_exported_class_alias( self ):
        return 'exported_class_t'
    exported_class_alias = property( _get_exported_class_alias )

    def create_function_type_alias_code( self, exported_class_alias=None ):
        raise NotImplementedError()

    def _create_impl( self ):
        if self.declaration.already_exposed:
            return ''

        result = []

        if not self.works_on_instance:
            exported_class_alias = None
            if declarations.templates.is_instantiation( self.declaration.parent.name ):
                exported_class_alias = self.exported_class_alias
                result.append( 'typedef %s %s;' % ( self.parent.decl_identifier, exported_class_alias ) )
                result.append( os.linesep )
            result.append( self.create_function_type_alias_code(exported_class_alias) )
            result.append( os.linesep * 2 )

        result.append( self.create_def_code() + '( ' )
        result.append( os.linesep + self.indent( '"%s"' % self.alias ) )

        result.append( self.param_sep() )
        result.append( self.create_function_ref_code( not self.works_on_instance ) )

        if self.declaration.use_keywords:
            keywd_args = self.create_keywords_args()
            if keywd_args:
                result.append( self.param_sep() )
                result.append( keywd_args )

        if self.declaration.call_policies:
            c_p_code = self.create_call_policies()
            if c_p_code:
                result.append( self.param_sep() )
                result.append( c_p_code )
        else:
            result.append( os.linesep + self.indent( '/* undefined call policies */', 2 ) )

        doc = self.create_doc()
        if doc:
            result.append( self.param_sep() )
            result.append( doc )

        result.append( ' )' )
        if not self.works_on_instance:
            result.append( ';' )

        if not self.works_on_instance:
            #indenting and adding scope
            code = ''.join( result )
            result = [ '{ //%s' % declarations.full_name( self.declaration ) ]
            result.append( os.linesep * 2 )
            result.append( self.indent( code ) )
            result.append( os.linesep * 2 )
            result.append( '}' )

        return ''.join( result )


class calldef_wrapper_t( code_creator.code_creator_t
                         , declaration_based.declaration_based_t):
    def __init__(self, function ):
        code_creator.code_creator_t.__init__( self )
        declaration_based.declaration_based_t.__init__( self, declaration=function )

    def override_identifier(self):
        return algorithm.create_identifier( self, '::boost::python::override' )

    def function_call_args( self ):
        arg_utils = calldef_utils.argument_utils_t( self.declaration, algorithm.make_id_creator( self ) )
        return arg_utils.call_args()

    def args_declaration( self ):
        arg_utils = calldef_utils.argument_utils_t( self.declaration, algorithm.make_id_creator( self ) )
        return arg_utils.args_declaration()

    def wrapped_class_identifier( self ):
        return algorithm.create_identifier( self, declarations.full_name( self.declaration.parent ) )

    def unoverriden_function_body( self ):
        return 'throw std::logic_error("%s");' % self.declaration.non_overridable_reason

    def throw_specifier_code( self ):
        if self.declaration.does_throw:
            if not self.declaration.exceptions:
                return ''
            else:
                exceptions = map( lambda exception: 
                                        algorithm.create_identifier( self, declarations.full_name( exception ) )
                                  , self.declaration.exceptions )
                return ' throw( ' + self.PARAM_SEPARATOR.join( exceptions ) + ' )'
        else:
            return ' throw()'

class free_function_t( calldef_t ):
    def __init__( self, function ):
        calldef_t.__init__( self, function=function )
        self.works_on_instance = False

    def create_def_code( self ):
        return self.def_identifier()

    def create_function_type_alias_code( self, exported_class_alias=None  ):
        return 'typedef ' + self.declaration.function_type().create_typedef( self.function_type_alias ) + ';'

    def create_function_ref_code(self, use_function_alias=False):
        if use_function_alias:
            return '%s( &%s )' \
                   % ( self.function_type_alias, declarations.full_name( self.declaration ) )
        elif self.declaration.create_with_signature:
            return '(%s)( &%s )' \
                   % ( self.declaration.function_type().decl_string
                       , declarations.full_name( self.declaration ) )
        else:
            return '&%s' % declarations.full_name( self.declaration )


class mem_fun_t( calldef_t ):
    def __init__( self, function ):
        calldef_t.__init__( self, function=function )

    def create_function_type_alias_code( self, exported_class_alias=None  ):
        ftype = self.declaration.function_type()
        return 'typedef %s;' % ftype.create_typedef( self.function_type_alias, exported_class_alias )

    def create_function_ref_code(self, use_function_alias=False):
        if use_function_alias:
            return '%s( &%s )' \
                   % ( self.function_type_alias, declarations.full_name( self.declaration ) )
        elif self.declaration.create_with_signature:
            return '(%s)( &%s )' \
                   % ( self.declaration.function_type().decl_string
                       , declarations.full_name( self.declaration ) )
        else:
            return '&%s' % declarations.full_name( self.declaration )


class mem_fun_pv_t( calldef_t ):
    def __init__( self, function, wrapper ):
        calldef_t.__init__( self, function=function, wrapper=wrapper )

    def create_function_type_alias_code( self, exported_class_alias=None  ):
        ftype = self.declaration.function_type()
        return 'typedef %s;' % ftype.create_typedef( self.function_type_alias, exported_class_alias )

    def create_function_ref_code(self, use_function_alias=False):
        if use_function_alias:
            return '%s( %s(&%s) )' \
                   % ( self.pure_virtual_identifier()
                       , self.function_type_alias
                       , declarations.full_name( self.declaration ) )
        elif self.declaration.create_with_signature:
            return '%s( (%s)(&%s) )' \
                   % ( self.pure_virtual_identifier()
                       , self.declaration.function_type().decl_string
                       , declarations.full_name( self.declaration ) )
        else:
            return '%s( &%s )' \
                   % ( self.pure_virtual_identifier()
                       , declarations.full_name( self.declaration ) )

class mem_fun_pv_wrapper_t( calldef_wrapper_t ):
    def __init__( self, function ):
        calldef_wrapper_t.__init__( self, function=function )

    def create_declaration(self):
        template = 'virtual %(return_type)s %(name)s( %(args)s )%(constness)s%(throw)s'

        constness = ''
        if self.declaration.has_const:
            constness = ' const '

        return template % {
            'return_type' : self.declaration.return_type.decl_string
            , 'name' : self.declaration.name
            , 'args' : self.args_declaration()
            , 'constness' : constness
            , 'throw' : self.throw_specifier_code()
        }

    def create_body( self ):
        if not self.declaration.overridable:
            return self.unoverriden_function_body()
        template = []
        precall_code = self.declaration.override_precall_code
        if precall_code:
            template.append( os.linesep.join( precall_code ) )
        template.append( '%(override)s func_%(alias)s = this->get_override( "%(alias)s" );' )
        template.append( '%(return_)sfunc_%(alias)s( %(args)s );')
        template = os.linesep.join( template )

        return_ = ''
        if not declarations.is_void( self.declaration.return_type ):
            return_ = 'return '

        return template % {
            'override' : self.override_identifier()
            , 'alias' : self.declaration.alias
            , 'return_' : return_
            , 'args' : self.function_call_args()
        }

    def _create_impl(self):
        answer = [ self.create_declaration() + '{' ]
        answer.append( self.indent( self.create_body() ) )
        answer.append( '}' )
        return os.linesep.join( answer )

class mem_fun_v_t( calldef_t ):
    def __init__( self, function, wrapper=None ):
        calldef_t.__init__( self, function=function, wrapper=wrapper )
        self.default_function_type_alias = 'default_' + self.function_type_alias

    def create_function_type_alias_code( self, exported_class_alias=None ):
        result = []

        ftype = self.declaration.function_type()
        result.append( 'typedef %s;' % ftype.create_typedef( self.function_type_alias, exported_class_alias )  )
        if self.wrapper:
            result.append( os.linesep )
            ftype = self.wrapper.function_type()
            result.append( 'typedef %s;' % ftype.create_typedef( self.default_function_type_alias ) )
        return ''.join( result )

    def create_doc(self):
        return None

    def create_function_ref_code(self, use_function_alias=False):
        result = []
        if use_function_alias:
            result.append( '%s(&%s)'
                           % ( self.function_type_alias, declarations.full_name( self.declaration ) ) )
            if self.wrapper:
                result.append( self.param_sep() )
                result.append( '%s(&%s)'
                                % ( self.default_function_type_alias, self.wrapper.default_full_name() ) )
        elif self.declaration.create_with_signature:
            result.append( '(%s)(&%s)'
                           % ( self.declaration.function_type().decl_string
                               , declarations.full_name( self.declaration ) ) )
            if self.wrapper:
                result.append( self.param_sep() )
                result.append( '(%s)(&%s)'
                               % ( self.wrapper.function_type().decl_string, self.wrapper.default_full_name() ) )
        else:
            result.append( '&%s'% declarations.full_name( self.declaration ) )
            if self.wrapper:
                result.append( self.param_sep() )
                result.append( '&%s' % self.wrapper.default_full_name() )
        return ''.join( result )

class mem_fun_v_wrapper_t( calldef_wrapper_t ):
    def __init__( self, function ):
        calldef_wrapper_t.__init__( self, function=function )

    def default_full_name(self):
        return self.parent.full_name + '::default_' + self.declaration.alias

    def function_type(self):
        return declarations.member_function_type_t(
                return_type=self.declaration.return_type
                , class_inst=declarations.dummy_type_t( self.parent.full_name )
                , arguments_types=map( lambda arg: arg.type, self.declaration.arguments )
                , has_const=self.declaration.has_const )

    def create_declaration(self, name, has_virtual=True):
        template = '%(virtual)s%(return_type)s %(name)s( %(args)s )%(constness)s %(throw)s'

        virtual = 'virtual '
        if not has_virtual:
            virtual = ''

        constness = ''
        if self.declaration.has_const:
            constness = ' const '

        return template % {
            'virtual' : virtual
            , 'return_type' : self.declaration.return_type.decl_string
            , 'name' : name
            , 'args' : self.args_declaration()
            , 'constness' : constness
            , 'throw' : self.throw_specifier_code()
        }

    def create_virtual_body(self):
        template = []
        precall_code = self.declaration.override_precall_code
        if precall_code:
            template.append( os.linesep.join( precall_code ) )
        template.append( 'if( %(override)s func_%(alias)s = this->get_override( "%(alias)s" ) )' )
        template.append( self.indent('%(return_)sfunc_%(alias)s( %(args)s );') )
        template.append( 'else' )
        template.append( self.indent('%(return_)sthis->%(wrapped_class)s::%(name)s( %(args)s );') )
        template = os.linesep.join( template )

        return_ = ''
        if not declarations.is_void( self.declaration.return_type ):
            return_ = 'return '

        return template % {
            'override' : self.override_identifier()
            , 'name' : self.declaration.name
            , 'alias' : self.declaration.alias
            , 'return_' : return_
            , 'args' : self.function_call_args()
            , 'wrapped_class' : self.wrapped_class_identifier()
        }

    def create_default_body(self):
        function_call = declarations.call_invocation.join( self.declaration.name
                                                           , [ self.function_call_args() ] )
        body = self.wrapped_class_identifier() + '::' + function_call + ';'
        if not declarations.is_void( self.declaration.return_type ):
            body = 'return ' + body
        precall_code = self.declaration.default_precall_code
        if precall_code:
            body = os.linesep.join( precall_code ) + os.linesep + body
        return body


    def create_function(self):
        answer = [ self.create_declaration(self.declaration.name) + '{' ]
        answer.append( self.indent( self.create_virtual_body() ) )
        answer.append( '}' )
        return os.linesep.join( answer )

    def create_default_function( self ):
        answer = [ self.create_declaration('default_' + self.declaration.alias, False) + '{' ]
        answer.append( self.indent( self.create_default_body() ) )
        answer.append( '}' )
        return os.linesep.join( answer )

    def _create_impl(self):
        answer = [ self.create_function() ]
        answer.append( os.linesep )
        answer.append( self.create_default_function() )
        return os.linesep.join( answer )


class mem_fun_protected_t( calldef_t ):
    def __init__( self, function, wrapper ):
        calldef_t.__init__( self, function=function, wrapper=wrapper )

    def create_function_type_alias_code( self, exported_class_alias=None  ):
        ftype = self.wrapper.function_type()
        return 'typedef ' + ftype.create_typedef( self.function_type_alias ) + ';'

    def create_function_ref_code(self, use_function_alias=False):
        if use_function_alias:
            return '%s( &%s )' \
                   % ( self.function_type_alias, self.wrapper.full_name() )
        elif self.declaration.create_with_signature:
            return '(%s)(&%s)' \
                   % ( self.wrapper.function_type().decl_string, self.wrapper.full_name() )
        else:
            return '&%s' % self.wrapper.full_name()

class mem_fun_protected_wrapper_t( calldef_wrapper_t ):
    def __init__( self, function ):
        calldef_wrapper_t.__init__( self, function=function )

    def full_name(self):
        return '::'.join( [self.parent.full_name, self.declaration.name] )

    def function_type(self):
        return declarations.member_function_type_t(
                return_type=self.declaration.return_type
                , class_inst=declarations.dummy_type_t( self.parent.full_name )
                , arguments_types=map( lambda arg: arg.type, self.declaration.arguments )
                , has_const=self.declaration.has_const )

    def create_declaration(self, name):
        template = '%(return_type)s %(name)s( %(args)s )%(constness)s%(throw)s'

        constness = ''
        if self.declaration.has_const:
            constness = ' const '

        return template % {
            'return_type' : self.declaration.return_type.decl_string
            , 'name' : name
            , 'args' : self.args_declaration()
            , 'constness' : constness
            , 'throw' : self.throw_specifier_code()
        }

    def create_body(self):
        tmpl = '%(return_)s%(wrapped_class)s::%(name)s( %(args)s );'

        return_ = ''
        if not declarations.is_void( self.declaration.return_type ):
            return_ = 'return '

        return tmpl % {
            'name' : self.declaration.name
            , 'return_' : return_
            , 'args' : self.function_call_args()
            , 'wrapped_class' : self.wrapped_class_identifier()
        }

    def create_function(self):
        answer = [ self.create_declaration(self.declaration.name) + '{' ]
        answer.append( self.indent( self.create_body() ) )
        answer.append( '}' )
        return os.linesep.join( answer )

    def _create_impl(self):
        return self.create_function()



class mem_fun_protected_s_t( calldef_t ):
    def __init__( self, function, wrapper ):
        calldef_t.__init__( self, function=function, wrapper=wrapper )

    def create_function_type_alias_code( self, exported_class_alias=None  ):
        ftype = self.wrapper.function_type()
        return 'typedef %s;' % ftype.create_typedef( self.function_type_alias )

    def create_function_ref_code(self, use_function_alias=False):
        if use_function_alias:
            return '%s( &%s )' \
                   % ( self.function_type_alias, self.wrapper.full_name() )
        elif self.declaration.create_with_signature:
            return '(%s)(&%s)' \
                   % ( self.wrapper.function_type().decl_string, self.wrapper.full_name() )
        else:
            return '&%s' % self.wrapper.full_name()

class mem_fun_protected_s_wrapper_t( calldef_wrapper_t ):
    def __init__( self, function ):
        calldef_wrapper_t.__init__( self, function=function )

    def full_name(self):
        return '::'.join( [self.parent.full_name, self.declaration.name] )

    def function_type(self):
        return declarations.free_function_type_t(
                return_type=self.declaration.return_type
                , arguments_types=map( lambda arg: arg.type, self.declaration.arguments ) )

    def create_declaration(self, name):
        template = 'static %(return_type)s %(name)s( %(args)s )%(throw)s'

        return template % {
            'return_type' : self.declaration.return_type.decl_string
            , 'name' : name
            , 'args' : self.args_declaration()
            , 'throw' : self.throw_specifier_code()
        }

    def create_body(self):
        tmpl = '%(return_)s%(wrapped_class)s::%(name)s( %(args)s );'

        return_ = ''
        if not declarations.is_void( self.declaration.return_type ):
            return_ = 'return '

        return tmpl % {
            'name' : self.declaration.name
            , 'return_' : return_
            , 'args' : self.function_call_args()
            , 'wrapped_class' : self.wrapped_class_identifier()
        }

    def create_function(self):
        answer = [ self.create_declaration(self.declaration.name) + '{' ]
        answer.append( self.indent( self.create_body() ) )
        answer.append( '}' )
        return os.linesep.join( answer )

    def _create_impl(self):
        return self.create_function()

class mem_fun_protected_v_t( calldef_t ):
    def __init__( self, function, wrapper ):
        calldef_t.__init__( self, function=function, wrapper=wrapper )

    def create_function_type_alias_code( self, exported_class_alias=None  ):
        ftype = self.wrapper.function_type()
        return 'typedef %s;' % ftype.create_typedef( self.function_type_alias )

    def create_function_ref_code(self, use_function_alias=False):
        if use_function_alias:
            return '%s( &%s )' \
                   % ( self.function_type_alias, self.wrapper.full_name() )
        elif self.declaration.create_with_signature:
            return '(%s)(&%s)' \
                   % ( self.wrapper.function_type().decl_string, self.wrapper.full_name() )
        else:
            return '&%s' % self.wrapper.full_name()

class mem_fun_protected_v_wrapper_t( calldef_wrapper_t ):
    def __init__( self, function):
        calldef_wrapper_t.__init__( self, function=function )

    def full_name(self):
        return self.parent.full_name + '::' + self.declaration.name

    def function_type(self):
        return declarations.member_function_type_t(
                return_type=self.declaration.return_type
                , class_inst=declarations.dummy_type_t( self.parent.full_name )
                , arguments_types=map( lambda arg: arg.type, self.declaration.arguments )
                , has_const=self.declaration.has_const )

    def create_declaration(self, name):
        template = 'virtual %(return_type)s %(name)s( %(args)s )%(constness)s%(throw)s'

        constness = ''
        if self.declaration.has_const:
            constness = ' const '

        return template % {
            'return_type' : self.declaration.return_type.decl_string
            , 'name' : name
            , 'args' : self.args_declaration()
            , 'constness' : constness
            , 'throw' : self.throw_specifier_code()
        }

    def create_virtual_body(self):
        template = []
        
        precall_code = self.declaration.override_precall_code
        if precall_code:
            template.append( os.linesep.join( precall_code ) )

        template.append( 'if( %(override)s func_%(alias)s = this->get_override( "%(alias)s" ) )' )
        template.append( self.indent('%(return_)sfunc_%(alias)s( %(args)s );') )
        template.append( 'else' )
        template.append( self.indent('%(return_)sthis->%(wrapped_class)s::%(name)s( %(args)s );') )
        template = os.linesep.join( template )

        return_ = ''
        if not declarations.is_void( self.declaration.return_type ):
            return_ = 'return '

        return template % {
            'override' : self.override_identifier()
            , 'name' : self.declaration.name
            , 'alias' : self.declaration.alias
            , 'return_' : return_
            , 'args' : self.function_call_args()
            , 'wrapped_class' : self.wrapped_class_identifier()
        }

    def create_function(self):
        answer = [ self.create_declaration(self.declaration.name) + '{' ]
        answer.append( self.indent( self.create_virtual_body() ) )
        answer.append( '}' )
        return os.linesep.join( answer )

    def _create_impl(self):
        return self.create_function()

class mem_fun_protected_pv_t( calldef_t ):
    def __init__( self, function, wrapper ):
        calldef_t.__init__( self, function=function, wrapper=wrapper )

    def create_function_type_alias_code( self, exported_class_alias=None  ):
        ftype = self.wrapper.function_type()
        return 'typedef %s;' % ftype.create_typedef( self.function_type_alias )

    def create_function_ref_code(self, use_function_alias=False):
        if use_function_alias:
            return '%s( &%s )' \
                   % ( self.function_type_alias, self.wrapper.full_name() )
        elif self.declaration.create_with_signature:
            return '(%s)(&%s)' \
                   % ( self.wrapper.function_type().decl_string, self.wrapper.full_name() )
        else:
            return '&%s' % self.wrapper.full_name()

class mem_fun_protected_pv_wrapper_t( calldef_wrapper_t ):
    def __init__( self, function):
        calldef_wrapper_t.__init__( self, function=function )

    def full_name(self):
        return self.parent.full_name + '::' + self.declaration.name

    def function_type(self):
        return declarations.member_function_type_t(
                return_type=self.declaration.return_type
                , class_inst=declarations.dummy_type_t( self.parent.full_name )
                , arguments_types=map( lambda arg: arg.type, self.declaration.arguments )
                , has_const=self.declaration.has_const )

    def create_declaration(self):
        template = 'virtual %(return_type)s %(name)s( %(args)s )%(constness)s%(throw)s'

        constness = ''
        if self.declaration.has_const:
            constness = ' const '

        return template % {
            'return_type' : self.declaration.return_type.decl_string
            , 'name' : self.declaration.name
            , 'args' : self.args_declaration()
            , 'constness' : constness
            , 'throw' : self.throw_specifier_code()
        }

    def create_body( self ):
        if not self.declaration.overridable:
            return self.unoverriden_function_body()

        template = []

        precall_code = self.declaration.override_precall_code
        if precall_code:
            template.append( os.linesep.join( precall_code ) )

        template.append( '%(override)s func_%(alias)s = this->get_override( "%(alias)s" );' )
        template.append( '%(return_)sfunc_%(alias)s( %(args)s );')
        template = os.linesep.join( template )

        return_ = ''
        if not declarations.is_void( self.declaration.return_type ):
            return_ = 'return '

        return template % {
            'override' : self.override_identifier()
            , 'alias' : self.declaration.alias
            , 'return_' : return_
            , 'args' : self.function_call_args()
        }

    def _create_impl(self):
        answer = [ self.create_declaration() + '{' ]
        answer.append( self.indent( self.create_body() ) )
        answer.append( '}' )
        return os.linesep.join( answer )

class mem_fun_private_v_wrapper_t( calldef_wrapper_t ):
    def __init__( self, function):
        calldef_wrapper_t.__init__( self, function=function )

    def full_name(self):
        return self.parent.full_name + '::' + self.declaration.name

    def function_type(self):
        return declarations.member_function_type_t(
                return_type=self.declaration.return_type
                , class_inst=declarations.dummy_type_t( self.parent.full_name )
                , arguments_types=map( lambda arg: arg.type, self.declaration.arguments )
                , has_const=self.declaration.has_const )

    def create_declaration(self):
        template = 'virtual %(return_type)s %(name)s( %(args)s )%(constness)s%(throw)s'

        constness = ''
        if self.declaration.has_const:
            constness = ' const '

        return template % {
            'return_type' : self.declaration.return_type.decl_string
            , 'name' : self.declaration.name
            , 'args' : self.args_declaration()
            , 'constness' : constness
            , 'throw' : self.throw_specifier_code()
        }

    def create_body( self ):
        if not self.declaration.overridable:
            return self.unoverriden_function_body()

        template = []
        
        precall_code = self.declaration.override_precall_code
        if precall_code:
            template.append( os.linesep.join( precall_code ) )

        template.append( '%(override)s func_%(alias)s = this->get_override( "%(alias)s" );' )
        template.append( '%(return_)sfunc_%(alias)s( %(args)s );')
        template = os.linesep.join( template )

        return_ = ''
        if not declarations.is_void( self.declaration.return_type ):
            return_ = 'return '

        return template % {
            'override' : self.override_identifier()
            , 'alias' : self.declaration.alias
            , 'return_' : return_
            , 'args' : self.function_call_args()
        }

    def _create_impl(self):
        answer = [ self.create_declaration() + '{' ]
        answer.append( self.indent( self.create_body() ) )
        answer.append( '}' )
        return os.linesep.join( answer )

mem_fun_private_pv_wrapper_t = mem_fun_private_v_wrapper_t

class constructor_t( calldef_t ):
    """
    Creates boost.python code needed to expose constructor.
    """
    def __init__(self, constructor, wrapper=None ):
        calldef_t.__init__( self, function=constructor, wrapper=wrapper )

    def _create_arg_code( self, arg ):
        temp = arg.type
        if declarations.is_const( temp ):
            #By David Abrahams:
            #Function parameters declared consts are ignored by C++
            #except for the purpose of function definitions
            temp = declarations.remove_const( temp )
        return algorithm.create_identifier( self, temp.decl_string )

    def _generate_definition_args(self):
        answer = []
        optionals = []
        for arg in self.declaration.arguments:
            if arg.default_value or optionals:
                optionals.append( self._create_arg_code( arg ) )
            else:
                answer.append( self._create_arg_code( arg ) )

        optionals_str = ''
        if optionals:
            optionals_str = algorithm.create_identifier( self, '::boost::python::optional' )
            optionals_str = optionals_str + '< ' + ', '.join( optionals ) + ' >'
            answer.append( optionals_str )
        return ', '.join( answer )

    def create_init_code(self):
        init_identifier = algorithm.create_identifier( self, '::boost::python::init' )
        args = [ self._generate_definition_args() ]
        answer = [ '%s' % declarations.templates.join( init_identifier, args ) ]
        answer.append( '(' )
        keywords_args = None
        if self.declaration.use_keywords:
            keywords_args = self.create_keywords_args()
            answer.append( '%s' % keywords_args )
        if self.documentation:
            if keywords_args:
                answer.append( ', ' )
            answer.append( self.documentation )
        answer.append( ')' )
        if self.declaration.call_policies and not self.declaration.call_policies.is_default():
            answer.append('[%s]' % self.declaration.call_policies.create( self ) )
        return ''.join( answer )

    def _create_impl( self ):
        code = 'def( %s )' % self.create_init_code()
        if not self.works_on_instance:
            code = self.parent.class_var_name + '.' + code + ';'
        return code

class static_method_t( declaration_based.declaration_based_t
                       , registration_based.registration_based_t ):
    """
    Creates boost.python code that expose member function as static function.
    """
    def __init__(self, function, function_code_creator=None ):
        registration_based.registration_based_t.__init__( self )
        declaration_based.declaration_based_t.__init__( self, declaration=function )

        self._function_code_creator = function_code_creator

    def _get_function_code_creator(self):
        return self._function_code_creator
    def _set_function_code_creator(self, new_function_code_creator ):
        self._function_code_creator = new_function_code_creator
    function_code_creator = property( _get_function_code_creator, _set_function_code_creator )

    def _create_impl( self ):
        return 'staticmethod( "%s" )' % self.function_code_creator.alias

class constructor_wrapper_t( calldef_wrapper_t ):
    """
    Creates C++ code that builds wrapper arround exposed constructor.
    """

    def __init__( self, constructor ):
        calldef_wrapper_t.__init__( self, function=constructor )

    def _create_declaration(self):
        result = []
        result.append( self.parent.wrapper_alias )
        result.append( '(' )
        args = []
        if not self.target_configuration.boost_python_has_wrapper_held_type \
           or self.declaration.parent.require_self_reference:
            args.append( 'PyObject* self' )
        args_decl = self.args_declaration()
        if args_decl:
            args.append( args_decl )
        result.append( ', '.join( args ) )
        result.append( ' )' )
        return ''.join( result )

    def _create_constructor_call( self ):
        answer = [ algorithm.create_identifier( self, self.parent.declaration.decl_string ) ]
        answer.append( '( ' )
        arg_utils = calldef_utils.argument_utils_t( self.declaration, algorithm.make_id_creator( self ) )
        params = arg_utils.call_args()
        answer.append( params )
        if params:
            answer.append(' ')
        answer.append( ')' )
        return ''.join( answer )

    def _create_impl(self):
        answer = [ self._create_declaration() ]
        answer.append( ': ' + self._create_constructor_call() )
        answer.append( '  , ' +  self.parent.boost_wrapper_identifier + '(){' )
        if( self.declaration.is_copy_constructor ):
            answer.append( self.indent( '// copy constructor' ) )
        elif not self.declaration.arguments:
            answer.append( self.indent( '// null constructor' ) )
        else:
            answer.append( self.indent( '// constructor' ) )
        answer.append( self.declaration.body )
        answer.append( '}' )
        return os.linesep.join( answer )

#There is something I don't understand
#There are usecases when boost.python requeres
#constructor for wrapper class from exposed class
#I should understand this more
class copy_constructor_wrapper_t( code_creator.code_creator_t
                                  , declaration_based.declaration_based_t ):
    """
    Creates wrapper class constructor from wrapped class instance.
    """
    def __init__( self, constructor ):
        code_creator.code_creator_t.__init__( self )
        declaration_based.declaration_based_t.__init__( self, declaration=constructor )

    def _create_declaration(self):
        result = []
        result.append( self.parent.declaration.wrapper_alias )
        result.append( '(' )
        if not self.target_configuration.boost_python_has_wrapper_held_type \
           or self.declaration.parent.require_self_reference:
            result.append( 'PyObject* self, ' )
        declarated = declarations.declarated_t( self.declaration.parent )
        const_decl = declarations.const_t( declarated )
        const_ref_decl = declarations.reference_t( const_decl )
        identifier = algorithm.create_identifier( self, const_ref_decl.decl_string )
        result.append( identifier + ' arg' )
        result.append( ' )' )
        return ''.join( result )

    def _create_constructor_call( self ):
        answer = [ algorithm.create_identifier( self, self.parent.declaration.decl_string ) ]
        answer.append( '( arg )' )
        return ''.join( answer )

    def _create_impl(self):
        answer = [ self._create_declaration() ]
        answer.append( ': ' + self._create_constructor_call() )
        answer.append( '  , ' +  self.parent.boost_wrapper_identifier + '(){' )
        answer.append( self.indent( '// copy constructor' ) )
        answer.append( self.indent( self.parent.declaration.copy_constructor_body ) )
        answer.append( '}' )
        return os.linesep.join( answer )


class null_constructor_wrapper_t( code_creator.code_creator_t
                                  , declaration_based.declaration_based_t ):
    """
    Creates wrapper for compiler generated null constructor.
    """
    def __init__( self, constructor ):
        code_creator.code_creator_t.__init__( self )
        declaration_based.declaration_based_t.__init__( self, declaration=constructor )
        
    def _create_constructor_call( self ):
        return algorithm.create_identifier( self, self.parent.declaration.decl_string ) + '()'

    def _create_impl(self):
        answer = [ self.parent.declaration.wrapper_alias + '(' ]
        if not self.target_configuration.boost_python_has_wrapper_held_type \
           or self.declaration.parent.require_self_reference:
            answer[0] = answer[0] + 'PyObject* self'
        answer[0] = answer[0] + ')'
        answer.append( ': ' + self._create_constructor_call() )
        answer.append( '  , ' +  self.parent.boost_wrapper_identifier + '(){' )
        answer.append( self.indent( '// null constructor' ) )
        answer.append( self.indent( self.parent.declaration.null_constructor_body ) )
        answer.append( '}' )
        return os.linesep.join( answer )

#in python all operators are members of class, while in C++
#you can define operators that are not.
class operator_t( registration_based.registration_based_t
                  , declaration_based.declaration_based_t ):
    """
    Creates boost.python code needed to expose supported subset of C++ operators.
    """
    class SELF_POSITION:
        FIRST = 'first'
        SECOND = 'second'
        BOTH = 'both'

    def __init__(self, operator ):
        registration_based.registration_based_t.__init__( self )
        declaration_based.declaration_based_t.__init__( self, declaration=operator )

    def _call_type_constructor( self, type ):
        x = declarations.remove_reference( type )
        x = declarations.remove_cv( x )
        other = algorithm.create_identifier( self, '::boost::python::other' )
        type_ = algorithm.create_identifier( self, x.decl_string )
        return declarations.templates.join( other, [ type_ ] ) + '()'

    def _findout_self_position(self):
        assert not declarations.is_unary_operator( self.declaration )
        decompose_type = declarations.decompose_type
        parent_decl_string = self.parent.declaration.decl_string
        arg0 = decompose_type( self.declaration.arguments[0].type )[-1].decl_string
        if isinstance( self.declaration, declarations.member_operator_t ):
            if parent_decl_string == arg0:
                return self.SELF_POSITION.BOTH
            else:
                return self.SELF_POSITION.FIRST #may be wrong in case ++, --, but any way boost.python does not expose them
        #now we deal with non global operators
        arg1 = decompose_type( self.declaration.arguments[1].type )[-1].decl_string
        if arg0 == arg1:
            assert parent_decl_string == arg0 #in this case I have bug in module creator
            return operator_t.SELF_POSITION.BOTH
        elif arg0 != arg1 and arg0 == parent_decl_string:
            return operator_t.SELF_POSITION.FIRST
        elif arg0 != arg1 and arg1 == parent_decl_string:
            return operator_t.SELF_POSITION.SECOND
        else:
            assert not "Unable to find out boost::python::self position. " + str( self.declaration )

    def _create_binary_operator(self):
        self_identifier = algorithm.create_identifier( self, '::boost::python::self' )

        if self.declaration.symbol == '<<':
            str_identifier = algorithm.create_identifier( self, '::boost::python::self_ns::str' )
            return '%s( %s )' % ( str_identifier, self_identifier )
        
        answer = [ None, self.declaration.symbol, None ]
        self_position = self._findout_self_position()
        if self_position == self.SELF_POSITION.FIRST:
            answer[0] = self_identifier
            type_ = None
            if len( self.declaration.arguments ) == 2:
                type_ = self.declaration.arguments[1].type
            else:
                type_ = self.declaration.arguments[0].type
            answer[2] = self._call_type_constructor( type_ )
        elif self_position == self.SELF_POSITION.SECOND:
            answer[0] = self._call_type_constructor(self.declaration.arguments[0].type )
            answer[2] = self_identifier
        else:
            answer[0] = self_identifier
            answer[2] = self_identifier
        return ' '.join( answer )

    def _create_unary_operator(self):
        return self.declaration.symbol + algorithm.create_identifier( self, '::boost::python::self' )

    def _create_impl( self ):
        code = None
        if declarations.is_binary_operator( self.declaration ):
            code = self._create_binary_operator()
        else:
            code = self._create_unary_operator()
        return 'def( %s )' % code

class casting_operator_t( registration_based.registration_based_t
                          , declaration_based.declaration_based_t ):
    """
    Creates boost.python code needed to register type conversions( implicitly_convertible )
    """
    def __init__( self, operator ):
        registration_based.registration_based_t.__init__( self )
        declaration_based.declaration_based_t.__init__( self, declaration=operator )

    def _create_impl(self):
        #TODO add comment in case of non const operator
        implicitly_convertible = algorithm.create_identifier( self, '::boost::python::implicitly_convertible' )
        from_arg = algorithm.create_identifier( self
                                                , declarations.full_name( self.declaration.parent ) )

        to_arg = algorithm.create_identifier( self
                                              , self.declaration.return_type.decl_string )
        return declarations.templates.join(implicitly_convertible
                                           , [ from_arg , to_arg ] )  \
               + '();'

class casting_member_operator_t( registration_based.registration_based_t
                                 , declaration_based.declaration_based_t ):
    """
    Creates boost.python code needed to register casting operators. For some
    operators Pythonic name is given: __int__, __long__, __float__, __str__
    """

    def __init__( self, operator ):
        registration_based.registration_based_t.__init__( self )
        declaration_based.declaration_based_t.__init__( self, declaration=operator )

    def _create_impl(self):
        template = 'def( "%(function_name)s", &%(class_name)s::operator %(destination_type)s %(call_policies)s%(doc)s )'

        class_name = algorithm.create_identifier( self
                                                , declarations.full_name( self.declaration.parent ) )

        policies = ''
        if self.declaration.call_policies:
            if not self.declaration.call_policies.is_default():
                policies = ',' + self.declaration.call_policies.create( self )
        else:
            policies = '/*, undefined call policies */'

        doc = ''
        if self.documentation:
            doc = ', %s' % self.documentation

        return template % { 'function_name' : self.declaration.alias
                            , 'class_name' : class_name
                            , 'destination_type' : self.declaration.return_type.decl_string
                            , 'call_policies' : policies
                            , 'doc' : doc
               }

class casting_constructor_t( registration_based.registration_based_t
                             , declaration_based.declaration_based_t ):
    """
    Creates boost.python code needed to register type conversions( implicitly_convertible ).
    This case treat situation when class has public non explicit constuctor from
    another type.
    """
    def __init__( self, constructor ):
        registration_based.registration_based_t.__init__( self )
        declaration_based.declaration_based_t.__init__( self, declaration=constructor )

    def _create_impl(self):
        implicitly_convertible = algorithm.create_identifier( self, '::boost::python::implicitly_convertible' )
        from_arg = algorithm.create_identifier( self
                                                ,  self.declaration.arguments[0].type.decl_string)

        to_arg = algorithm.create_identifier( self
                                              , declarations.full_name( self.declaration.parent ) )
        return declarations.templates.join(implicitly_convertible
                                           , [ from_arg , to_arg ] )  \
               + '();'



class calldef_overloads_class_t( code_creator.code_creator_t ):
    def __init__( self, functions ):
        #precondition: all member functions belong to same class and
        #they all have same alias, otherwise it does not makes sense
        code_creator.code_creator_t.__init__( self )
        self._functions = functions
        self._functions.sort() #I need this for "stabble" code generation
        self._max_fun = None #function with maximal number of arguments

    @property
    def functions( self ):
        return self._functions

    def min_max_num_of_args( self ):
        #returns tuple( minimal, maximal ) number of arguments
        min_ = None
        max_ = 0
        for f in self.functions:
            f_max = len( f.arguments )
            f_min = f_max - len( filter( lambda arg: arg.default_value, f.arguments ) )
            if None is min_:
                min_ = f_min
            else:
                min_ = min( min_, f_min )
            max_tmp = max( max_, f_max )
            if max_ < max_tmp:
                max_ = max_tmp
                self._max_fun = f
        return ( min_, max_ )

    @property
    def max_function( self ):
        if not self._max_fun:
            initialize_max_fun_var = self.min_max_num_of_args()
        return self._max_fun

    @property
    def max_function_identifier( self ):
        return algorithm.create_identifier( self, declarations.full_name( self.max_function ) )

    @property
    def alias( self ):
        return self.functions[0].alias

    @property
    def parent_decl( self ):
        return self.functions[0].parent

    @property
    def name( self ):
        return '%s_%s_overloads' % ( self.parent_decl.alias, self.alias )

class mem_fun_overloads_class_t( calldef_overloads_class_t ):
    def __init__( self, mem_funs ):
        #precondition: all member functions belong to same class and
        #they all have same alias, otherwise it does not makes sense
        calldef_overloads_class_t.__init__( self, mem_funs )

    def _create_impl(self):
        if self.max_function.already_exposed:
            return ''

        min_, max_ = self.min_max_num_of_args()
        return "BOOST_PYTHON_MEMBER_FUNCTION_OVERLOADS( %(overloads_cls)s, %(fun)s, %(min)d, %(max)d )" \
               % {   'overloads_cls' : self.name
                   , 'fun' : self.max_function_identifier
                   , 'min' : min_
                   , 'max' : max_
               }

class free_fun_overloads_class_t( calldef_overloads_class_t ):
    def __init__( self, free_funs ):
        #precondition: all member functions belong to same class and
        #they all have same alias, otherwise it does not makes sense
        calldef_overloads_class_t.__init__( self, free_funs )

    def _create_impl(self):
        if self.max_function.already_exposed:
            return ''

        min_, max_ = self.min_max_num_of_args()
        return "BOOST_PYTHON_FUNCTION_OVERLOADS( %(overloads_cls)s, %(fun)s, %(min)d, %(max)d )" \
               % {   'overloads_cls' : self.name
                   , 'fun' : self.max_function_identifier
                   , 'min' : min_
                   , 'max' : max_
               }

class calldef_overloads_t( registration_based.registration_based_t ):
    def __init__( self, overloads_class ):
        registration_based.registration_based_t.__init__( self )
        self._overloads_class = overloads_class

    @property
    def overloads_class( self ):
        return self._overloads_class

    def create_def_code( self ):
        raise NotImplementedError()

    def create_end_def_code( self ):
        raise NotImplementedError()

    def create_keywords_args(self):
        result = [ algorithm.create_identifier( self, '::boost::python::args' ) ]
        result.append( '( ' )
        args = []
        for arg in self.overloads_class.max_function.arguments:
            if 0 < len( args ):
                args.append( self.PARAM_SEPARATOR )
            args.append( '"%s"' % arg.name )
        result.extend( args )
        result.append( ' )' )
        return ''.join( result )

    def _get_function_type_alias( self ):
        return self.overloads_class.alias + '_function_type'
    function_type_alias = property( _get_function_type_alias )

    def create_function_type_alias_code( self, exported_class_alias=None ):
        raise NotImplementedError()

    def create_overloads_cls( self ):
        result = [ self.overloads_class.name ]
        result.append( '( ' )
        result.append( os.linesep + self.indent( self.create_keywords_args(), 3 ) )
        if self.overloads_class.max_function.documentation:
            result.append( os.linesep + self.indent( self.PARAM_SEPARATOR, 3 ) )
            result.append( self.overloads_class.max_function.documentation )
        result.append( ' )' )
        if self.overloads_class.max_function.call_policies \
           and not self.overloads_class.max_function.call_policies.is_default():
            result.append( os.linesep + self.indent('', 3) )
            result.append('[ %s ]' % self.overloads_class.max_function.call_policies.create( self ) )
        return ''.join( result )

    def _create_impl(self):
        result = []
        if not self.works_on_instance:
            exported_class_alias = None
            if declarations.templates.is_instantiation( self.overloads_class.max_function.parent.name ):
                exported_class_alias = self.exported_class_alias
                result.append( 'typedef %s %s;' % ( self.parent.decl_identifier, exported_class_alias ) )
                result.append( os.linesep )
            result.append( self.create_function_type_alias_code(exported_class_alias) )
            result.append( os.linesep * 2 )

        result.append( self.create_def_code() + '( ' )
        result.append( os.linesep + self.indent( '"%s"' % self.overloads_class.alias ) )

        result.append( os.linesep + self.indent( self.PARAM_SEPARATOR ) )
        result.append( self.create_function_ref_code( not self.works_on_instance ) )

        result.append( os.linesep + self.indent( self.PARAM_SEPARATOR ) )
        result.append( self.create_overloads_cls() )

        result.append( ' )' )
        result.append( self.create_end_def_code() )

        if not self.works_on_instance:
            #indenting and adding scope
            code = ''.join( result )
            result = [ '{ //%s' % declarations.full_name( self.overloads_class.max_function ) ]
            result.append( os.linesep * 2 )
            result.append( self.indent( code ) )
            result.append( os.linesep * 2 )
            result.append( '}' )

        return ''.join( result )

class mem_fun_overloads_t( calldef_overloads_t ):
    def __init__( self, overloads_class ):
        calldef_overloads_t.__init__( self, overloads_class )

    def create_def_code( self ):
        if not self.works_on_instance:
            return '%s.def' % self.parent.class_var_name
        else:
            return 'def'

    def create_end_def_code( self ):
        if not self.works_on_instance:
            return ';'
        else:
            return ''

    def create_function_type_alias_code( self, exported_class_alias=None  ):
        ftype = self.overloads_class.max_function.function_type()
        return 'typedef %s;' % ftype.create_typedef( self.function_type_alias, exported_class_alias )

    def create_function_ref_code(self, use_function_alias=False):
        fname = declarations.full_name( self.overloads_class.max_function )
        if use_function_alias:
            return '%s( &%s )' % ( self.function_type_alias, fname )
        elif self.overloads_class.max_function.create_with_signature:
            return '(%s)( &%s )' % ( self.overloads_class.max_function.function_type().decl_string, fname )
        else:
            return '&%s' % fname


class free_fun_overloads_t( calldef_overloads_t ):
    def __init__( self, overloads_class ):
        calldef_overloads_t.__init__( self, overloads_class )

    def create_def_code( self ):
        return algorithm.create_identifier( self, '::boost::python::def' )

    def create_end_def_code( self ):
        return ';'

    def create_function_type_alias_code( self, exported_class_alias=None  ):
        ftype = self.overloads_class.max_function.function_type()
        return 'typedef %s;' % ftype.create_typedef( self.function_type_alias, exported_class_alias )

    def create_function_ref_code(self, use_function_alias=False):
        fname = declarations.full_name( self.overloads_class.max_function )
        if use_function_alias:
            return '%s( &%s )' % ( self.function_type_alias, fname )
        elif self.overloads_class.max_function.create_with_signature:
            return '(%s)( &%s )' % ( self.overloads_class.max_function.function_type().decl_string, fname )
        else:
            return '&%s' % fname
