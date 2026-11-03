#include <iostream>

int main()
{
    int values[5] = {1, 2, 3, 4, 5};
    int* current = values;
    int* end = values + 5;
    int sum = 0;

    while (current < end) // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-12-2]
    {
        sum += *current;
        ++current;
    }

    std::cout << sum << '\n';
    return 0;
}
