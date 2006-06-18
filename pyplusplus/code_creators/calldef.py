# Copyright 2004 Roman Yakovenko.
# Distributed under the Boost Software License, Version 1.0. (See
# accompanying file LICENSE_1_0.txt or copy at
# http://www.boost.org/LICENSE_1_0.txt)

import os
import algorithm
import declaration_based
import class_declaration
from pygccxml import declarations

#virtual functions that returns const reference to something
#could not be overriden by Python. The reason is simple: 
#in boost::python::override::operator(...) result of marshaling 
#(Python 2 C++) is saved on stack, after functions returns the result
#will be reference to no where - access violetion.
#For example see temporal variable tester


#TODO:
#Add to docs:
#public memebr functions - call, override, call base implementation
#protected member functions - call, override
#private - override 

class calldef_t( declaration_based.declaration_based_t):
    def __init__(self, function, wrapper=None, parent=None ):
        declaration_based.declaration_based_t.__init__( self
                                                        , declaration=function
                                                        , parent=parent )
        self._wrapper = wrapper   
            
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
        return os.linesep + self.indent( self.PARAM_SEPARATOR, 2 )

    def keywords_args(self):
        boost_arg = algorithm.create_identifier( self, '::boost::python::arg' )
        boost_obj = algorithm.create_identifier( self, '::boost::python::object' )
        result = ['( ']
        for arg in self.declaration.arguments:
            if 1 < len( result ):
                result.append( self.PARAM_SEPARATOR )
            result.append( boost_arg )
            result.append( '("%s")' % arg.name )
            if self.declaration.use_default_arguments and arg.default_value:
                if not declarations.is_pointer( arg.type ) or arg.default_value != '0':
                    result.append( '=%s' % arg.default_value )
                else:
                    result.append( '=%s()' % boost_obj )
        result.append( ' )' )
        return ''.join( result )
    
class calldef_wrapper_t( declaration_based.declaration_based_t):    
    def __init__(self, function, parent=None ):
        declaration_based.declaration_based_t.__init__( self
                                                        , declaration=function
                                                        , parent=parent )

    def argument_name( self, index ):
        arg = self.declaration.arguments[ index ]
        if arg.name:
            return arg.name
        else:
            return 'p%d' % index

    #def args_declaration( self ):
        #args = []
        #for index, arg in enumerate( self.declaration.arguments ):
            #args.append( arg.type.decl_string + ' ' + self.argument_name(index) )
        #if len( args ) == 1:
            #return args[ 0 ] 
        #return ', '.join( args )
    
    def args_declaration( self ):
        args = []
        boost_obj = algorithm.create_identifier( self, '::boost::python::object' )
        for index, arg in enumerate( self.declaration.arguments ):
            result = arg.type.decl_string + ' ' + self.argument_name(index)
            if arg.default_value:
                if not declarations.is_pointer( arg.type ) or arg.default_value != '0':
                    result += '=%s' % arg.default_value
                else:
                    result += '=%s()' % boost_obj
            args.append( result )
        if len( args ) == 1:
            return args[ 0 ]
        return ', '.join( args )
    
    def override_identifier(self):
        return algorithm.create_identifier( self, '::boost::python::override' )

    def function_call_args( self ):
        params = []
        for index in range( len( self.declaration.arguments ) ):
            arg_type = declarations.remove_alias( self.declaration.arguments[index].type )
            arg_base_type = declarations.base_type( arg_type )
            if declarations.is_fundamental( arg_base_type ):
                params.append( self.argument_name( index ) )
            elif declarations.is_reference( arg_type ) \
                 and not declarations.is_const( arg_type ) \
                 and not declarations.is_enum( arg_base_type ):
                params.append( 'boost::ref(%s)' % self.argument_name( index ) )
            elif declarations.is_pointer( arg_type ) \
                 and not declarations.is_fundamental( arg_type.base ) \
                 and not declarations.is_enum( arg_base_type ):
                params.append( 'boost::python::ptr(%s)' % self.argument_name( index ) )
            else:
                params.append( self.argument_name( index ) )
        return ', '.join( params )
    
    def wrapped_class_identifier( self ):
        return algorithm.create_identifier( self, self.declaration.parent.decl_string )
    
    def unoverriden_function_body( self ):
        msg = r'This function could not be overriden in Python!'
        msg = msg + 'Reason: function returns reference to local variable!'
        return 'throw std::logic_error("%s");' % msg

    def throw_specifier_code( self ):
        if not self.declaration.exceptions:
            return ''
        exceptions = map( lambda exception: 
                            algorithm.create_identifier( self, declarations.full_name( exception ) )
                          , self.declaration.exceptions )
        return ' throw( ' + self.PARAM_SEPARATOR.join( exceptions ) + ' )'
    
class free_function_t( calldef_t ):   
    def __init__( self, function, parent=None ):
        calldef_t.__init__( self, function=function, parent=parent )
    
    def _create_impl(self):
        param_sep = self.param_sep()
        
        result = [ self.def_identifier() ]
        result.append( '(' )
        result.append( '"%s"' % self.alias )
        result.append( param_sep )
        if self.declaration.create_with_signature:
            result.append( '(%s)( &%s )' 
                           %( self.declaration.function_type().decl_string
                              , declarations.full_name( self.declaration ) ) )
        else:
            result.append( '&%s' % declarations.full_name( self.declaration ) )
        
        if self.declaration.use_keywords:
            result.append( param_sep )            
            result.append( self.keywords_args() )
        if self.declaration.call_policies:
            result.append( param_sep )            
            result.append( self.declaration.call_policies.create( self ) )
        else:
            result.append( os.linesep + self.indent( '/* undefined call policies */', 2 ) )             
        result.append( ' );' )
        return ''.join( result )

class mem_fun_t( calldef_t ):   
    def __init__( self, function, parent=None ):
        calldef_t.__init__( self, function=function, parent=parent )
    
    def _create_impl(self):
        param_sep = self.param_sep()
        
        result = [ 'def' ]
        result.append( '(' )
        result.append( '"%s"' % self.alias )
        result.append( param_sep )
        if self.declaration.create_with_signature:
            result.append( '(%s)( &%s )' 
                           %( self.declaration.function_type().decl_string
                              , declarations.full_name( self.declaration ) ) )
        else:
            result.append( '&%s' % declarations.full_name( self.declaration ) )
        
        if self.declaration.use_keywords:
            result.append( param_sep )            
            result.append( self.keywords_args() )
        if self.declaration.call_policies:
            result.append( param_sep )            
            result.append( self.declaration.call_policies.create( self ) )
        else:
            result.append( os.linesep + self.indent( '/* undefined call policies */', 2 ) )             
        result.append( ' )' )
        return ''.join( result )


class mem_fun_pv_t( calldef_t ):   
    def __init__( self, function, wrapper, parent=None ):
        calldef_t.__init__( self, function=function, wrapper=wrapper, parent=parent )
    
    def _create_impl(self):
        param_sep = self.param_sep()
        
        result = [ 'def' ]
        result.append( '(' )
        result.append( '"%s"' % self.alias )
        result.append( param_sep )
        if self.declaration.create_with_signature:
            result.append( '%s( (%s)(&%s) )'
                           % ( self.pure_virtual_identifier()
                               , self.declaration.function_type().decl_string
                               , declarations.full_name( self.declaration ) ) )
        else:
            result.append( '%s( &%s )'
                           % ( self.pure_virtual_identifier()
                               , declarations.full_name( self.declaration ) ) )
            
        if self.declaration.use_keywords:
            result.append( param_sep )            
            result.append( self.keywords_args() )
        if self.declaration.call_policies:
            result.append( param_sep )            
            result.append( self.declaration.call_policies.create( self ) )
        else:
            result.append( os.linesep + self.indent( '/* undefined call policies */', 2 ) )             
        result.append( ' )' )
        return ''.join( result )

class mem_fun_pv_wrapper_t( calldef_wrapper_t ):
    def __init__( self, function, parent=None):
        calldef_wrapper_t.__init__( self, function=function, parent=parent )

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
        if declarations.is_reference( self.declaration.return_type ):
            return self.unoverriden_function_body()
        template = []
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
    def __init__( self, function, wrapper=None, parent=None ):
        calldef_t.__init__( self, function=function, wrapper=wrapper, parent=parent )
    
    def _create_impl(self):
        param_sep = self.param_sep()
        
        result = [ 'def' ]
        result.append( '(' )
        result.append( '"%s"' % self.alias )
        result.append( param_sep )
        if self.declaration.create_with_signature:
            result.append( '(%s)(&%s)'
                           % ( self.declaration.function_type().decl_string
                               , declarations.full_name( self.declaration ) ) )
            if self.wrapper:
                result.append( param_sep )
                result.append( '(%s)(&%s)' 
                               % ( self.wrapper.function_type().decl_string, self.wrapper.default_full_name() ) )
        else:
            result.append( '&%s'% declarations.full_name( self.declaration ) )
            if self.wrapper:
                result.append( param_sep )
                result.append( '&%s' % self.wrapper.default_full_name() )
            
        if self.declaration.use_keywords:
            result.append( param_sep )            
            result.append( self.keywords_args() )
        if self.declaration.call_policies:
            result.append( param_sep )            
            result.append( self.declaration.call_policies.create( self ) )
        else:
            result.append( os.linesep + self.indent( '/* undefined call policies */', 2 ) )             
        result.append( ' )' )
        return ''.join( result )

class mem_fun_v_wrapper_t( calldef_wrapper_t ):
    def __init__( self, function, parent=None):
        calldef_wrapper_t.__init__( self, function=function, parent=parent )

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
        template.append( 'if( %(override)s func_%(alias)s = this->get_override( "%(alias)s" ) )' )
        template.append( self.indent('%(return_)sfunc_%(alias)s( %(args)s );') )
        template.append( 'else' )
        template.append( self.indent('%(return_)s%(wrapped_class)s::%(name)s( %(args)s );') )
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
    def __init__( self, function, wrapper, parent=None ):
        calldef_t.__init__( self, function=function, wrapper=wrapper, parent=parent )
    
    def _create_impl(self):
        param_sep = self.param_sep()
        
        result = [ 'def' ]
        result.append( '(' )
        result.append( '"%s"' % self.alias )
        result.append( param_sep )
        if self.declaration.create_with_signature:
            result.append( '(%s)(&%s)' 
                               % ( self.wrapper.function_type().decl_string
                                   , self.wrapper.full_name() ) )
        else:
            result.append( '&%s' % self.wrapper.full_name() )
            
        if self.declaration.use_keywords:
            result.append( param_sep )            
            result.append( self.keywords_args() )
        if self.declaration.call_policies:
            result.append( param_sep )            
            result.append( self.declaration.call_policies.create( self ) )
        else:
            result.append( os.linesep + self.indent( '/* undefined call policies */', 2 ) )             
        result.append( ' )' )
        return ''.join( result )

class mem_fun_protected_wrapper_t( calldef_wrapper_t ):
    def __init__( self, function, parent=None):
        calldef_wrapper_t.__init__( self, function=function, parent=parent )

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
    def __init__( self, function, wrapper, parent=None ):
        calldef_t.__init__( self, function=function, wrapper=wrapper, parent=parent )
    
    def _create_impl(self):
        param_sep = self.param_sep()
        
        result = [ 'def' ]
        result.append( '(' )
        result.append( '"%s"' % self.alias )
        result.append( param_sep )
        if self.declaration.create_with_signature:
            result.append( '(%s)(&%s)' 
                               % ( self.wrapper.function_type().decl_string
                                   , self.wrapper.full_name() ) )
        else:
            result.append( '&%s' % self.wrapper.full_name() )
            
        if self.declaration.use_keywords:
            result.append( param_sep )            
            result.append( self.keywords_args() )
        if self.declaration.call_policies:
            result.append( param_sep )            
            result.append( self.declaration.call_policies.create( self ) )
        else:
            result.append( os.linesep + self.indent( '/* undefined call policies */', 2 ) )             
        result.append( ' )' )
        return ''.join( result )

class mem_fun_protected_s_wrapper_t( calldef_wrapper_t ):
    def __init__( self, function, parent=None):
        calldef_wrapper_t.__init__( self, function=function, parent=parent )

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
    def __init__( self, function, wrapper, parent=None ):
        calldef_t.__init__( self, function=function, wrapper=wrapper, parent=parent )
    
    def _create_impl(self):
        param_sep = self.param_sep()
        
        result = [ 'def' ]
        result.append( '(' )
        result.append( '"%s"' % self.alias )
        result.append( param_sep )
        if self.declaration.create_with_signature:
            result.append( '(%s)(&%s)' 
                           % ( self.wrapper.function_type().decl_string, self.wrapper.full_name() ) )
        else:
            result.append( '&%s' % self.wrapper.full_name() )
            
        if self.declaration.use_keywords:
            result.append( param_sep )            
            result.append( self.keywords_args() )
        if self.declaration.call_policies:
            result.append( param_sep )            
            result.append( self.declaration.call_policies.create( self ) )
        else:
            result.append( os.linesep + self.indent( '/* undefined call policies */', 2 ) )             
        result.append( ' )' )
        return ''.join( result )


class mem_fun_protected_v_wrapper_t( calldef_wrapper_t ):
    def __init__( self, function, parent=None):
        calldef_wrapper_t.__init__( self, function=function, parent=parent )

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
        template.append( 'if( %(override)s func_%(alias)s = this->get_override( "%(alias)s" ) )' )
        template.append( self.indent('%(return_)sfunc_%(alias)s( %(args)s );') )
        template.append( 'else' )
        template.append( self.indent('%(return_)s%(wrapped_class)s::%(name)s( %(args)s );') )
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
    def __init__( self, function, wrapper,parent=None ):
        calldef_t.__init__( self, function=function, wrapper=wrapper, parent=parent )
    
    def _create_impl(self):
        param_sep = self.param_sep()
        
        result = [ 'def' ]
        result.append( '(' )
        result.append( '"%s"' % self.alias )
        result.append( param_sep )
        if self.declaration.create_with_signature:
            result.append( '(%s)(&%s)'
                           % ( self.wrapper.function_type().decl_string
                               , self.wrapper.full_name() ) )
        else:
            result.append( '&%s' % self.wrapper.full_name() )
            
        if self.declaration.use_keywords:
            result.append( param_sep )            
            result.append( self.keywords_args() )
        if self.declaration.call_policies:
            result.append( param_sep )            
            result.append( self.declaration.call_policies.create( self ) )
        else:
            result.append( os.linesep + self.indent( '/* undefined call policies */', 2 ) )             
        result.append( ' )' )
        return ''.join( result )

class mem_fun_protected_pv_wrapper_t( calldef_wrapper_t ):
    def __init__( self, function, parent=None):
        calldef_wrapper_t.__init__( self, function=function, parent=parent )

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
        if declarations.is_reference( self.declaration.return_type ):
            return self.unoverriden_function_body()

        template = []
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
    def __init__( self, function, parent=None):
        calldef_wrapper_t.__init__( self, function=function, parent=parent )

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
        if declarations.is_reference( self.declaration.return_type ):
            return self.unoverriden_function_body()

        template = []
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


#class protected_helper_t( object ):
    #def __init__( self ):
        #object.__init__( self )

    #def wclass_inst_arg_type( self ):
        #inst_arg_type = declarations.declarated_t( self.declaration.parent )
        #if self.declaration.has_const:
            #inst_arg_type = declarations.const_t(inst_arg_type)
        #inst_arg_type = declarations.reference_t(inst_arg_type)
        #return inst_arg_type

    #def wclass_inst_arg( self ):
        #return self.wclass_inst_arg_type().decl_string + ' wcls_inst'


class constructor_t( declaration_based.declaration_based_t ):
    """
    Creates boost.python code needed to expose constructor.
    """
    def __init__(self, constructor, wrapper=None, parent=None ):
        declaration_based.declaration_based_t.__init__( self
                                                        , declaration=constructor
                                                        , parent=parent )
        self._wrapper = wrapper
        
    def _get_wrapper( self ):
        return self._wrapper
    def _set_wrapper( self, new_wrapper ):
        self._wrapper = new_wrapper
    wrapper = property( _get_wrapper, _set_wrapper )
        
    def _get_call_policies(self):
        return self.declaration.call_policies
    def _set_call_policies(self, call_policies):
        self.declaration.call_policies = call_policies
    call_policies = property( _get_call_policies, _set_call_policies )

    def _get_use_keywords(self):
        return self.declaration.use_keywords
    def _set_use_keywords(self, use_keywords):
        self.declaration.use_keywords = use_keywords
    use_keywords = property( _get_use_keywords, _set_use_keywords )

    def _get_use_default_arguments(self):
        return self.declaration.use_default_arguments
    def _set_use_default_arguments(self, use_default_arguments):
        self.declaration.use_default_arguments = use_default_arguments
    use_default_arguments = property( _get_use_default_arguments, _set_use_default_arguments )
        
    def _keywords_args(self):
        if not self.declaration.arguments:
            return ''        
        boost_arg = algorithm.create_identifier( self, '::boost::python::arg' )
        boost_obj = algorithm.create_identifier( self, '::boost::python::object' )
        result = ['( ']
        for arg in self.declaration.arguments:
            if 1 < len( result ):
                result.append( ', ' )
            result.append( boost_arg )
            result.append( '("%s")' % arg.name )
            if self.use_default_arguments and arg.default_value:
                if not declarations.is_pointer( arg.type ) or arg.default_value != '0':
                    result.append( '=%s' % arg.default_value )
                else:
                    result.append( '=%s()' % boost_obj )
        result.append( ' )' )
        return ''.join( result )        
        
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
        if self.use_keywords:
            answer.append( '(%s)' % self._keywords_args() )
        else:
            answer.append( '()' )
        if self.call_policies:
            answer.append('[%s]' % self.call_policies.create( self ) )
        #I think it better not to print next line
        #else:
        #    answer.append( '/*[ undefined call policies ]*/' )
        return ''.join( answer )
    
    def _create_impl( self ):
        return 'def( %s )' % self.create_init_code()

class static_method_t( declaration_based.declaration_based_t ):
    """
    Creates boost.python code that expose member function as static function.
    """
    def __init__(self, function, function_code_creator=None, parent=None ):
        declaration_based.declaration_based_t.__init__( self
                                                        , declaration=function
                                                        , parent=parent )

        self._function_code_creator = function_code_creator
        
    def _get_function_code_creator(self):
        return self._function_code_creator
    def _set_function_code_creator(self, new_function_code_creator ):
        self._function_code_creator = new_function_code_creator
    function_code_creator = property( _get_function_code_creator, _set_function_code_creator )
        
    def _create_impl( self ):
        return 'staticmethod( "%s" )' % self.function_code_creator.alias
    
class constructor_wrapper_t( declaration_based.declaration_based_t ):
    """
    Creates C++ code that builds wrapper arround exposed constructor.
    """

    def __init__( self, constructor, parent=None ):
        declaration_based.declaration_based_t.__init__( self
                                                        , declaration=constructor
                                                        , parent=parent )

    def argument_name( self, index ):
        arg = self.declaration.arguments[ index ]
        if arg.name:
            return arg.name
        else:
            return 'p%d' % index
        
    def _create_declaration(self):
        result = []
        result.append( self.parent.wrapper_alias )
        result.append( '(' )
        args = []
        if self.parent.held_type and not self.target_configuration.boost_python_has_wrapper_held_type:
            args.append( 'PyObject*' )
        for index, arg in enumerate( self.declaration.arguments ):
            arg_text = arg.type.decl_string + ' ' + self.argument_name(index)
            if arg.default_value:
                arg_text = arg_text + '=%s' % arg.default_value
            args.append( arg_text )
        result.append( ', '.join( args ) )
        result.append( ' )' )
        return ''.join( result )
    
    def _create_constructor_call( self ):
        answer = [ algorithm.create_identifier( self, self.parent.declaration.decl_string ) ]
        answer.append( '( ' )
        params = []
        for index in range( len( self.declaration.arguments ) ):
            params.append( self.argument_name( index ) )
        answer.append( ', '.join( params ) )
        if params:
            answer.append(' ')
        answer.append( ')' )
        return ''.join( answer )
    
    def _create_impl(self):
        answer = [ self._create_declaration() ]
        answer.append( ': ' + self._create_constructor_call() )
        answer.append( '  , ' +  self.parent.boost_wrapper_identifier + '()' )
        answer.append( '{   // Normal constructor' )
        answer.append( self.declaration.body )
        answer.append( '}' )
        return os.linesep.join( answer )

#There is something I don't understand
#There are usecases when boost.python requeres
#constructor for wrapper class from exposed class
#I should understand this more
class copy_constructor_wrapper_t( declaration_based.declaration_based_t ):
    """
    Creates wrapper class constructor from wrapped class instance.
    """
    def __init__( self, class_inst, parent=None ):
        declaration_based.declaration_based_t.__init__( self
                                                        , declaration=class_inst
                                                        , parent=parent )

    def _create_declaration(self):
        result = []
        result.append( self.parent.wrapper_alias )
        result.append( '(' )
        if self.parent.held_type and not self.target_configuration.boost_python_has_wrapper_held_type:
            result.append( 'PyObject*, ' )
        declarated = declarations.declarated_t( self.declaration )
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
        answer.append( self.indent( self.declaration.copy_constructor_body ) )
        answer.append( '}' )
        return os.linesep.join( answer )


class null_constructor_wrapper_t( declaration_based.declaration_based_t ):
    """
    Creates wrapper for compiler generated null constructor.
    """    
    def __init__( self, class_inst, parent=None ):
        declaration_based.declaration_based_t.__init__( self
                                                        , declaration=class_inst
                                                        , parent=parent )

    def _create_constructor_call( self ):
        return algorithm.create_identifier( self, self.parent.declaration.decl_string ) + '()'
    
    def _create_impl(self):
        answer = [ self.parent.wrapper_alias + '(' ]
        if self.parent.held_type and not self.target_configuration.boost_python_has_wrapper_held_type:
            answer[0] = answer[0] + 'PyObject*'
        answer[0] = answer[0] + ')'
        answer.append( ': ' + self._create_constructor_call() )
        answer.append( '  , ' +  self.parent.boost_wrapper_identifier + '(){' )
        answer.append( self.indent( '// null constructor' ) )
        answer.append( self.indent( self.declaration.null_constructor_body ) )
        answer.append( '}' )
        return os.linesep.join( answer )

#in python all operators are members of class, while in C++
#you can define operators that are not.
class operator_t( declaration_based.declaration_based_t ):    
    """
    Creates boost.python code needed to expose supported subset of C++ operators.
    """
    class SELF_POSITION:
        FIRST = 'first'
        SECOND = 'second'
        BOTH = 'both'
        
    def __init__(self, operator, parent=None ):
        declaration_based.declaration_based_t.__init__( self
                                                        , declaration=operator
                                                        , parent=parent )
    
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
            assert 0 #I have bug some where

    def _create_binary_operator(self):
        answer = [ None, self.declaration.symbol, None ]
        self_identifier = algorithm.create_identifier( self, '::boost::python::self' )
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

class casting_operator_t( declaration_based.declaration_based_t ):
    """
    Creates boost.python code needed to register type conversions( implicitly_convertible )
    """
    def __init__( self, operator, parent=None ):
        declaration_based.declaration_based_t.__init__( self
                                                        , declaration=operator
                                                        , parent=parent )

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

class casting_member_operator_t( declaration_based.declaration_based_t ):
    """
    Creates boost.python code needed to register casting operators. For some 
    operators Pythonic name is given: __int__, __long__, __float__, __str__
    """
      
    def __init__( self, operator, parent=None ):
        declaration_based.declaration_based_t.__init__( self
                                                        , declaration=operator
                                                        , parent=parent )
        self._call_policies = None

    def _create_impl(self):
        template = 'def( "%(function_name)s", &%(class_name)s::operator %(destination_type)s %(call_policies)s )'
        
        class_name = algorithm.create_identifier( self
                                                , declarations.full_name( self.declaration.parent ) )
        
        policies = '/*, undefined call policies */' 
        if self.declaration.call_policies:
            policies = ',' + self.declaration.call_policies.create( self )
        
        return template % { 'function_name' : self.declaration.alias
                            , 'class_name' : class_name
                            , 'destination_type' : self.declaration.return_type.decl_string
                            , 'call_policies' : policies
               }

class casting_constructor_t( declaration_based.declaration_based_t ):
    """
    Creates boost.python code needed to register type conversions( implicitly_convertible ).
    This case treat situation when class has public non explicit constuctor from
    another type.
    """
    def __init__( self, constructor, parent=None ):
        declaration_based.declaration_based_t.__init__( self
                                                        , declaration=constructor
                                                        , parent=parent )

    def _create_impl(self):
        implicitly_convertible = algorithm.create_identifier( self, '::boost::python::implicitly_convertible' )
        from_arg = algorithm.create_identifier( self
                                                ,  self.declaration.arguments[0].type.decl_string)
        
        to_arg = algorithm.create_identifier( self
                                              , declarations.full_name( self.declaration.parent ) )
        return declarations.templates.join(implicitly_convertible
                                           , [ from_arg , to_arg ] )  \
               + '();'



