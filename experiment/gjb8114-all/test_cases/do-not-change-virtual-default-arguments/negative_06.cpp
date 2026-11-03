#include <iostream>

int fallback_target = 42;

class Base {
public:
    virtual ~Base() = default;
    virtual void setTarget(int *target = nullptr);
};

void Base::setTarget(int *target) {
    if (target != nullptr) {
        *target = 1;
    }
}

class Derived : public Base {
public:
    void setTarget(int *target = &fallback_target) override; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-2-4-1]
};

void Derived::setTarget(int *target) {
    if (target != nullptr) {
        *target = 2;
    }
}

int main() {
    Derived derived;
    Base &ref = derived;
    int local = 0;
    derived.setTarget(&local);
    ref.setTarget();
    std::cout << local + fallback_target << '\n';
    return 0;
}
