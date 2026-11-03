#include <cstddef>

int main()
{
    int x = 1;
    int y = 2;
    std::size_t ilen = sizeof(x = y); // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-6-13]
    (void)ilen;
    return 0;
}
