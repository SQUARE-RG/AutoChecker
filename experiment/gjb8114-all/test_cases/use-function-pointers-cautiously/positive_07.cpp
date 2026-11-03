#include <functional>
#include <iostream>

int main() {
    int factor = 3;
    std::function<int(int)> transform = [factor](int value) { return value * factor; };
    int result = transform(7);
    std::cout << result << std::endl;
    return 0;
}
