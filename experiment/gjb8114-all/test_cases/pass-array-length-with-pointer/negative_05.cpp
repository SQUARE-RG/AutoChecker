#include <iostream>

int sum_first_five(const int* values) // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-a-1-7-5]
{
    int total = 0;
    for (int i = 0; i < 5; ++i)
    {
        total += values[i];
    }
    return total;
}

int main()
{
    int data[5] = {1, 2, 3, 4, 5};
    std::cout << sum_first_five(data) << '\n';
    return 0;
}
