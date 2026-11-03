#include <iostream>

using Handler = int (*)(int);

int identity(int value) {
    return value;
}

class Base {
public:
    virtual ~Base() = default;
    virtual int dispatch(Handler handler = nullptr) const {
        return handler ? handler(7) : 0;
    }
};

class Derived : public Base {
public:
    int dispatch(Handler handler = nullptr) const override {
        return handler ? handler(9) : 1;
    }
};

int main() {
    Derived d;
    Base& b = d;
    int r1 = b.dispatch();
    int r2 = d.dispatch(&identity);
    return r1 + r2;
}
