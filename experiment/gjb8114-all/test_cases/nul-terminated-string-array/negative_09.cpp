#include <cstdio>
#include <string>

int main()
{
    std::string text = "yes";
    char buf[8];
    text.copy(buf, text.size()); // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-13-16]
    std::printf("%s\n", buf);
    return 0;
}
