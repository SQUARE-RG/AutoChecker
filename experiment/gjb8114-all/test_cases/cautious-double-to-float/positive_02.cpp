#include <iostream>

void takeDouble(double x) {
    std::cout << x << std::endl;
}

int main() {
    float f = 1.5f;
    takeDouble(f);
    return 0;
}
