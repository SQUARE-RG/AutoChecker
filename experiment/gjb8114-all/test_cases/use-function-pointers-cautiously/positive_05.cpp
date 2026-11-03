#include <iostream>

int main() {
    auto operation = [](int a, int b) { return a + b; };
    std::cout << operation(10, 20) << '\n';
    return 0;
}
