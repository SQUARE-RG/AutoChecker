#include <iostream>

int main() {
    int i = 0;
    int j = 0;

    if (0 == i)
    {
        j = 1;
        j += 2;
    }

    std::cout << j << std::endl;
    return 0;
}
