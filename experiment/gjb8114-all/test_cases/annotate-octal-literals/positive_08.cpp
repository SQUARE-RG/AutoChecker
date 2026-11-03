#include <iostream>

int main()
{
    int total = 0;
    for (int i = 1; i <= 010 /* octal */; ++i) {
        total += i;
    }
    std::cout << total << '\n';
    return 0;
}
