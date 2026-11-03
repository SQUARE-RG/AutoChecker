#include <iostream>

int main()
{
    int arr[5] = {1, 2, 3, 4, 5};
    int* first = &arr[0];
    int* last = &arr[4];
    int count = 0;

    for (int* p = first; p > last; ++p) // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-12-2]
    {
        ++count;
    }

    std::cout << count << '\n';
    return 0;
}
