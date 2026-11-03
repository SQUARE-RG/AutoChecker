#include <iostream>
#include <typeinfo>

class B {
public:
    B() = default;
    virtual ~B() = default;
    virtual int g() const { return 0; }
};

class D : public virtual B {
public:
    int g() const override { return 1; }
};

int main() {
    D d;
    B &b = d;
    try {
        const D &cd = dynamic_cast<const D &>(b);
        return cd.g() == 1 ? 0 : 1;
    } catch (const std::bad_cast &) {
        return 2;
    }
}
