#include <iostream>

int main() {
    int x = 1, y = 2, z = 3;
    x++;
    y--;
    z = z + y;
    std::cout << x << " " << y << " " << z << std::endl;
    return 0;
}
