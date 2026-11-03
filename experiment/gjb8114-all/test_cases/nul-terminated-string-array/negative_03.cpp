#include <cstdio>
#include <cstring>

int main()
{
    char msg[4];
    std::strncpy(msg, "abc", 3); // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-13-16]
    std::puts(msg);
    return 0;
}
