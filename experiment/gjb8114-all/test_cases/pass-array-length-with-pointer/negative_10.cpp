#include <cstddef>

void swapEnds(int* p) // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-a-1-7-5]
{
    int tmp = p[0];
    p[0] = p[5];
    p[5] = tmp;
}

int main()
{
    int data[6] = {1, 2, 3, 4, 5, 6};
    swapEnds(data);
    return data[0];
}
