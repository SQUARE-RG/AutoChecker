#include <iostream>

long int add(long int a, long int b);

int main()
{
    long int x = 3;
    long int y = 4;
    std::cout << add(x, y) << std::endl;
    return 0;
}

long add(long a, long b)
{
    return a + b;
}
