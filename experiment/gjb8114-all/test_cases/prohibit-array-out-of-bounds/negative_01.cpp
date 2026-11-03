#include <cstddef>

void comp(int a[], int n)
{
    for (int i = 0; i <= n; ++i)
    {
        a[i] = 0; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-6-8]
    }
}

int main()
{
    int array[100];
    comp(array, 100);
    return 0;
}
