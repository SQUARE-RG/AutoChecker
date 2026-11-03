#include <iostream>

int main()
{
    int values[3];
    values[0] = 10;
    values[1] = 20;
    values[2] = 30;
    int index = 0;
    int value = values[(index = 0, index + 1)]; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-a-1-6-6]
    std::cout << value << '\n';
    return 0;
}
