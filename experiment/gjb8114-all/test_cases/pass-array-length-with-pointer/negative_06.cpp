#include <iostream>

void scale_array(int values[8]) // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-a-1-7-5]
{
    for (int i = 0; i < 8; ++i)
    {
        values[i] *= 2;
    }
}

int main()
{
    int data[8] = {0, 1, 2, 3, 4, 5, 6, 7};
    scale_array(data);
    std::cout << data[7] << '\n';
    return 0;
}
