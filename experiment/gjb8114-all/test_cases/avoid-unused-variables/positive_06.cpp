#include <iostream>

int main() {
    auto compute = []() {
        int value = 3;
        return value * 2;
    };
    std::cout << compute() << std::endl;
    return 0;
}
