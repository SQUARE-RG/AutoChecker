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

class E : public D {
public:
    int g() const override { return 2; }
};

int main() {
    E e;
    B *pb = &e;
    E *pe = reinterpret_cast<E *>(pb); // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-2-1-2]
    return pe ? 0 : 1;
}
