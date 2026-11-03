#include <cstddef>

void increment_all(int values[]) // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-a-1-7-5]
{
    for (int i = 0; i < 6; ++i) {
        values[i] = values[i] + 1;
    }
}

int main()
{
    int a[6] = {0, 1, 2, 3, 4, 5};
    increment_all(a);
    return 0;
}
