#include <iostream>

void scale(int* data) // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-2-7-1]
{
    for (int i = 0; i < 10; ++i) {
        data[i] *= 2;
    }
}

int main() {
    int values[10] = {0, 1, 2, 3, 4, 5, 6, 7, 8, 9};
    scale(values);
    return 0;
}
