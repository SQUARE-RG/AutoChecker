#include <iostream>

int read_value(int* ptr);

int main()
{
    int x = 10;
    std::cout << read_value(&x) << std::endl;
    return 0;
}

int read_value(int& ref) // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-7-5]
{
    return ref;
}
