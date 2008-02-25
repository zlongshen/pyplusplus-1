// Copyright 2004 Roman Yakovenko.
// Distributed under the Boost Software License, Version 1.0. (See
// accompanying file LICENSE_1_0.txt or copy at
// http://www.boost.org/LICENSE_1_0.txt)

#ifndef __final_classes_to_be_exported_hpp__
#define __final_classes_to_be_exported_hpp__

#include <string>

namespace override_bug{

class A
{
  public:
   virtual int foo() const {return int('a');}
   virtual ~A(){}
};

class B: public A
{
};

inline int invoke_foo( const A& a ){
    return a.foo();
};

class Base1
{
public:
   virtual int eval_a() { return 1; }
   virtual int eval_b() { return 10; }
   virtual int eval_c() { return 100; }
   virtual int eval_d() { return 1000; }
   virtual int eval_e() { return 10000; }
};

class Derived2: public Base1
{
protected:
   virtual int eval_a() { return 2; }
   virtual int eval_b() { return 20; }
   virtual int eval_c() { return 200; }
   virtual int eval_d() { return 2000; }
   virtual int eval_e() { return 20000; }
};

class Derived3: public Derived2
{
};

int eval(Base1* obj) {
   return
      obj->eval_a()
    + obj->eval_b()
    + obj->eval_c()
    + obj->eval_d()
    + obj->eval_e()
    ;
}


struct AA
{
  public:
   virtual void do_smth(int& i) const { i = 'a' ;}
   virtual ~AA(){}
};

struct BB: public AA
{
    virtual void do_smth(int& i, int& j) const { i = j = 'b' ;}
};

} 

#endif//__final_classes_to_be_exported_hpp__

