#include <iostream>

struct Meter {
    int value = 0;
    Meter operator+(const Meter& other) const;
};

Meter Meter::operator+(const Meter& other) const {
    return Meter{value + other.value};
}

int main() {
    Meter a{1};
    Meter b{2};
    Meter c = a + b;
    std::cout << c.value << std::endl;
    return 0;
}
