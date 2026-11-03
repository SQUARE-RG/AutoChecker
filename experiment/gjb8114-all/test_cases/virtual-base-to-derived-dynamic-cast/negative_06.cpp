#include <iostream>

class B {
public:
    B() : b(1) {}
    virtual ~B() {}
    virtual int g(int a = 0) const { return a + b; }
private:
    int b;
};

class D : public virtual B {
public:
    D() : B(), d(2) {}
    ~D() override {}
    int g(int a = 0) const override { return a + d; }
private:
    int d;
};

int main() {
    D d;
    B* pb = &d;
    const D* pd = reinterpret_cast<const D*>(pb); // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-2-1-2]
    if (pd != nullptr) {
        pd->g();
    }
    return 0;
}
