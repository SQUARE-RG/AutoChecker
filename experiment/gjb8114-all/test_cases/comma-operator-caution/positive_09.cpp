#include <iostream>

int main() {
    int a = 0;
    int b = 0;
    bool condition = true;
    int result = condition ? (a = 1) : (b = 2);
    std::cout << result << std::endl;
    return 0;
}
