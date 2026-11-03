#include <iostream>

int combine(int a, int b)
{
    return a + b;
}

int main()
{
    volatile int flag = 3;
    int snapshot = flag;
    int result = combine(snapshot, snapshot);
    std::cout << result << std::endl;
    return 0;
}
