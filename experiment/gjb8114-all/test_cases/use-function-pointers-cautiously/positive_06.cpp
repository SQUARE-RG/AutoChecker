#include <iostream>

struct Adder {
    int operator()(int a, int b) const { return a + b; }
};

int main() {
    Adder add;
    std::cout << add(11, 22) << '\n';
    return 0;
}
