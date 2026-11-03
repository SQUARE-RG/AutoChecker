#include <iostream>

int main()
{
    int i = 0;
    int j = 3;
    for (; i < 3; ++i, --j) { // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-a-1-6-6]
        std::cout << i << ',' << j << '\n';
    }
    return 0;
}
