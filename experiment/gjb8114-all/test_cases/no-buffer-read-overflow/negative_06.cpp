#include <cstring>

int main()
{
    char small[2] = {'A', 'B'};
    char large[4] = {'A', 'B', 'C', 'D'};
    int result = std::memcmp(small, large, sizeof(large)); // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-6-14]
    (void)result;
    return 0;
}
