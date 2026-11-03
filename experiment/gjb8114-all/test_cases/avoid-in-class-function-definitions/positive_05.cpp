#include <iostream>

class Celsius {
public:
    explicit Celsius(double v);
    operator double() const;
private:
    double value;
};

Celsius::Celsius(double v) : value(v) {}
Celsius::operator double() const { return value; }

int main() {
    Celsius c(3.14);
    double d = c;
    std::cout << d << '\n';
    return 0;
}
