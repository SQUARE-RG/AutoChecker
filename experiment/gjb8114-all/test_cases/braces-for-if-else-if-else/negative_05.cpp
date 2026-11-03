#include <iostream>

int main() {
    int i = 0;
    int j = 0;

    if (0 == i)
    {
        j = 1;
    }
    else if (1 == i)
    {
        j = 3;
    }
    else
        j = 5; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-2-2]

    std::cout << j << std::endl;
    return 0;
}
