#include <cstdlib>

int main()
{
    int* arr = static_cast<int*>(std::malloc(4 * sizeof(int)));
    arr[0] = 5; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-3-8]
    std::free(arr);
    return 0;
}
