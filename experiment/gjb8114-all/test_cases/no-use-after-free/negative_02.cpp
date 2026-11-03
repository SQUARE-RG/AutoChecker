#include <cstdlib>

int main()
{
    int* arr = new int[4];
    arr[0] = 10;
    int first = arr[0];

    delete[] arr;

    first = arr[1]; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-6-16]
    return first;
}
