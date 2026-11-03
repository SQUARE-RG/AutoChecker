#include <iostream>

#define PI_VALUE 3.14159

double circle_area(double radius) {
    return PI_VALUE * radius * radius;
}

int main() {
    const double radius = 2.0;
    std::cout << circle_area(radius) << std::endl;
    return 0;
}
