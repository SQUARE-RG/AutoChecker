#include <cstring>

int main()
{
    char buffer[4] = {0};
    std::memset(buffer, 'A', 6); // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-6-15]
    return 0;
}
