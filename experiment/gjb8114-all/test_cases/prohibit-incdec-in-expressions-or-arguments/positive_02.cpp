#include <iostream>

int twice(int v) {
    return v * 2;
}

int main() {
    int x = 4;
    x++;
    int r = twice(x);
    x--;
    std::cout << r << " " << x << std::endl;
    return 0;
}
