#include <cstddef>

int main()
{
    int x = 1, y = 2;
    std::size_t ilen = sizeof(static_cast<int>(x = y)); // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-6-13]
    return 0;
}
