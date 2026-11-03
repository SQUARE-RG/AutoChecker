#include <iostream>

int main()
{
    int i = 0;
    int j = 3;
    for (; i < 3; ++i) {
        std::cout << i << ',' << j << '\n';
        --j;
    }
    return 0;
}
