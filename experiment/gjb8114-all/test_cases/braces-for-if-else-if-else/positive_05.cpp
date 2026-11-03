#include <iostream>

int main() {
    int i = 1;
    int j = 0;

    if (0 == i)
    {
        j = 1;
        j += 10;
    }
    else if (1 == i)
    {
        j = 3;
        j *= 2;
    }
    else
    {
        j = 5;
        j -= 1;
    }

    std::cout << j << std::endl;
    return 0;
}
