#include <iostream>

using Handler = int (*)(int);

int default_handler(int value) {
    return value + 1;
}

class Base {
public:
    virtual ~Base() = default;
    virtual int dispatch(Handler handler = nullptr) const {
        return handler ? handler(3) : 0;
    }
};

class Derived : public Base {
public:
    int dispatch(Handler handler = &default_handler) const override { // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-2-4-1]
        return handler ? handler(5) : 1;
    }
};

int main() {
    Derived d;
    Base& b = d;
    return b.dispatch() + d.dispatch();
}
