#include <iostream>

class Celsius {
public:
    explicit Celsius(double v);
    operator double() const { return value; } // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-a-2-7-1]
private:
    double value;
};

Celsius::Celsius(double v) : value(v) {}

int main() {
    Celsius c(3.14);
    double d = c;
    std::cout << d << '\n';
    return 0;
}
