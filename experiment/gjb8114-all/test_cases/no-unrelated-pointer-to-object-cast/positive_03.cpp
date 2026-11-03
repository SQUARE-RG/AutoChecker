#include <iostream>
using namespace std;

class Base {
public:
    virtual ~Base() {}
    virtual void foo() {}
};

class Derived : public Base {
public:
    void foo() override {}
    int x = 0;
};

int main() {
    Base* b = new Derived();
    Derived* d = dynamic_cast<Derived*>(b);
    if (d) {
        d->x = 1;
    }
    delete b;
    return 0;
}
