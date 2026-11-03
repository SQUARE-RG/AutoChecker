#include <iostream>

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
    const D &cd = reinterpret_cast<const D &>(b); // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-2-1-2]
    return cd.g() == 1 ? 0 : 1;
}
