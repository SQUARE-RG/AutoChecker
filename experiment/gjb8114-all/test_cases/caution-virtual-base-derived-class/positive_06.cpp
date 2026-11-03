class A {
public:
    virtual ~A() = default;
};

class B {
public:
    virtual ~B() = default;
};

class Derived : protected A, private B {
public:
    void f() {}
};

int main() {
    Derived d;
    d.f();
    return 0;
}
