#include <iostream>

int main() {
    int i = 2;
    int j = 0;

    if (0 == i)
        j = 1; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-2-2]
    else if (1 == i)
    {
        j = 3;
    }
    else
    {
        j = 5;
    }

    std::cout << j << std::endl;
    return 0;
}
