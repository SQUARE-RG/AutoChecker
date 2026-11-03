#include <iostream>

typedef int Triple[3];

int main() {
    Triple values = {1, 2, 3};
    std::cout << values[0] + values[1] + values[2] << std::endl;
    return 0;
}
