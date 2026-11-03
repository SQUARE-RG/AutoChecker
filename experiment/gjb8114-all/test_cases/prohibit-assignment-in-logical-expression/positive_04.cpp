#include <iostream>

int main()
{
    int sum = 0;
    for (int i = 0; i < 4; ++i) {
        sum += i;
    }
    std::cout << sum << std::endl;
    return 0;
}
