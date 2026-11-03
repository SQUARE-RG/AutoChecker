#include <iostream>

struct Number {
    int value;
};

Number operator+(const Number& lhs, const Number& rhs) {
    return Number{lhs.value + rhs.value};
}

int main() {
    int a = 1;
    int b = 2;
    int c = (a++, b);
    Number n1{3};
    Number n2{4};
    Number n3 = n1 + n2;
    std::cout << c << ' ' << n3.value << '\n';
    return 0;
}
