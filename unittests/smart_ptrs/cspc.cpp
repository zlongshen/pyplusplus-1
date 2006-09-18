// This file has been generated by Py++.

// Copyright 2004 Roman Yakovenko.
// Distributed under the Boost Software License, Version 1.0. (See
// accompanying file LICENSE_1_0.txt or copy at
// http://www.boost.org/LICENSE_1_0.txt)

#include "boost/python.hpp"
#include <assert.h>

//defining smart pointer class

template<class T> class smart_ptr_t {
protected:
	T* pRep;
	unsigned int* pUseCount;
public:

	smart_ptr_t()
    : pRep(0), pUseCount(0)
    {}

    //What will happen if rep is NULL? -> bug
	explicit smart_ptr_t(T* rep)
    : pRep(rep), pUseCount( new unsigned int(1) )
	{}

    template<class Y>
	smart_ptr_t(const smart_ptr_t<Y>& r)
    : pRep(0), pUseCount(0)
    {
		pRep = r.get();
		pUseCount = r.useCountPointer();
		if(pUseCount){
			++(*pUseCount);
		}
    }

    template< class Y>
	smart_ptr_t& operator=(const smart_ptr_t<Y>& r){
		if( pRep == r.pRep ){
			return *this;
	    }

		release();

		pRep = r.get();
		pUseCount = r.useCountPointer();
		if(pUseCount){
			++(*pUseCount);
		}
		return *this;
	}

	virtual ~smart_ptr_t() {
        release();
	}

	inline T& operator*() const {
	    assert(pRep); return *pRep;
	}

	inline T* operator->() const {
	    assert(pRep); return pRep;
	}

	inline T* get() const {
	    return pRep;
	}

	inline unsigned int* useCountPointer() const {
	    return pUseCount;
	}

	inline T* getPointer() const {
	    return pRep;
	}

protected:

    inline void release(void){
		bool destroyThis = false;

		if( pUseCount ){
			if( --(*pUseCount) == 0){
				destroyThis = true;
	        }
		}
		if (destroyThis){
			destroy();
	    }
    }

    virtual void destroy(void){
        delete pRep;
        delete pUseCount;
    }
};


//defining few classes and functions that should be exposed to Python


struct derived_t{
    virtual int get_value(void) const{
        return  11;
    }
};


int
val_get_value( smart_ptr_t<derived_t> a ){
    return a->get_value();
}

int
const_ref_get_value( const smart_ptr_t<derived_t>& a ){
    if( a.get() ){
        return a->get_value();
    }
    else{
        return -1;
    }
}

//Expose code

namespace bp = boost::python;

namespace boost{ namespace python{

    template<class T>
    inline T * get_pointer(smart_ptr_t<T> const& p){
        return p.get();
    }

    template <class T>
    struct pointee< smart_ptr_t<T> >{
        typedef T type;
    };

} }

BOOST_PYTHON_MODULE( cspc_ext ){

    bp::class_< derived_t, smart_ptr_t<derived_t> >( "derived_t" )
        .def( "get_value", &::derived_t::get_value );

    bp::def( "const_ref_get_value", &::const_ref_get_value );
    bp::def( "val_get_value", &::val_get_value );

}