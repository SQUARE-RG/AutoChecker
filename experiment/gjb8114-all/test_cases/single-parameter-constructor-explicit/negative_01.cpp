#include <iostream>

class Meter {
public:
    Meter();
    Meter(int value); // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-2-2-3]
    int getValue() const;
    ~Meter();
private:
    int value_;
};

Meter::Meter() : value_(0) {}
Meter::Meter(int value) : value_(value) {}
int Meter::getValue() const { return value_; }
Meter::~Meter() {}

void use(Meter m);

int main() {
    Meter m(10);
    use(10);
    return 0;
}

void use(Meter m) {
    std::cout << m.getValue() << std::endl;
}
