#include <iostream>
using namespace std;

class Base {
public:
    virtual ~Base() {}
    int b = 0;
};

class Derived : public Base {
public:
    int d = 0;
};

int main() {
    Base* base = new Derived();
    Derived* derived = reinterpret_cast<Derived*>(base);
    derived->d = 1;
    delete base;
    return 0;
}
