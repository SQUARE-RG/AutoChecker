#include <cstring>

int main()
{
    char dest[6] = {0};
    const char* src = "Hello";
    std::strncpy(dest, src, 7); // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-6-19]
    return 0;
}
