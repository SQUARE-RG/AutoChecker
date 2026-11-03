#include <algorithm>

int main()
{
    int dest[3] = {0, 0, 0};
    std::fill_n(dest, 5, 7); // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-6-15]
    return 0;
}
