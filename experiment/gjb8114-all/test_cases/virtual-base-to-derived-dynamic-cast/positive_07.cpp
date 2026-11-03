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
    E *pe = dynamic_cast<E *>(pb);
    if (pe) {
        return pe->g() == 2 ? 0 : 1;
    }
    return 1;
}
