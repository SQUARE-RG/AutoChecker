#include <cstring>

int main()
{
    char dest[5] = "Hi";
    const char* src = "abc";
    std::strncat(dest, src, 5); // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-6-19]
    return 0;
}
