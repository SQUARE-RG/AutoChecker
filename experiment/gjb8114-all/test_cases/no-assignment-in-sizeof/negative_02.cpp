#include <cstddef>

int main()
{
    int x = 1;
    std::size_t ilen = sizeof(x += 2); // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-6-13]
    (void)ilen;
    return 0;
}
