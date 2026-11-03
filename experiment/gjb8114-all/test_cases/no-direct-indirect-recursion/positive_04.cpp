#include <functional>
#include <iostream>

int main() {
    std::function<int(int)> increment = [](int value) { return value + 1; };
    std::function<int(int)> twice = [increment](int value) { return increment(value) * 2; };

    std::cout << twice(4) << '\n';
    return 0;
}
