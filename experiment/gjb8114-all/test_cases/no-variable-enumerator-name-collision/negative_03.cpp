#include <iostream>

enum Direction { north, south, east, west };

int travel(int north) // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-13-5]
{
    return north + 1;
}

int main()
{
    std::cout << travel(1) << '\n';
    return 0;
}
