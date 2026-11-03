#include <iostream>

class Base {
public:
    virtual ~Base() = default;
    virtual double compute(double x = 2.0, double y = 3.0) const;
};

double Base::compute(double x, double y) const {
    return x + y;
}

class Derived : public Base {
public:
    double compute(double x, double y) const override;
};

double Derived::compute(double x, double y) const {
    return x * y;
}

int main() {
    Derived d;
    Base& b = d;
    double r1 = b.compute();
    double r2 = d.compute(4.0, 5.0);
    std::cout << r1 << " " << r2 << std::endl;
    return 0;
}
