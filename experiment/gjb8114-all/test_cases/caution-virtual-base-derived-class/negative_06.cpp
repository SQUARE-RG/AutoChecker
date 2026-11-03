class A {
public:
    virtual ~A() = default;
};

class B {
public:
    virtual ~B() = default;
};

class Derived : virtual public A, public B {  // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-a-2-1-1]
public:
    void f() {}
};

int main() {
    Derived d;
    d.f();
    return 0;
}
