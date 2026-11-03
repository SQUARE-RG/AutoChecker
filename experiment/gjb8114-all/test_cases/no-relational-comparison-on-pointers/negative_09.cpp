#include <iostream>

int main()
{
    int values[] = {1, 2, 3, 4, 5};
    int* first = values;
    int* last = values + 4;
    int* current = first;
    int sum = 0;

    do
    {
        sum += *current;
        ++current;
    } while (current <= last); // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-12-2]

    std::cout << sum << std::endl;
    return 0;
}
