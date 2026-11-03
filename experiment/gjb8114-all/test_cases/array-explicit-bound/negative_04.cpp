#include <cstring>

int main()
{
    char greeting[] = "hello"; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-1-18]
    return std::strlen(greeting) == 5 ? 0 : 1;
}
