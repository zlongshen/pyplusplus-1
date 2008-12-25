# Copyright 2004-2008 Roman Yakovenko.
# Distributed under the Boost Software License, Version 1.0. (See
# accompanying file LICENSE_1_0.txt or copy at
# http://www.boost.org/LICENSE_1_0.txt)

import code_creator
import include_directories


class import_t(code_creator.code_creator_t):
    """Creates Python import directive"""
    def __init__( self, module_name ):
        code_creator.code_creator_t.__init__(self)
        self._module_name = module_name

    def _create_impl(self):
        return 'import %(module)s' % dict( module=self.module_name )

    def _get_system_headers_impl( self ):
        return []
