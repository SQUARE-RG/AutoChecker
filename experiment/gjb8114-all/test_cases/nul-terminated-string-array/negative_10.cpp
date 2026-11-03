#include <cstdio>
#include <vector>

int main()
{
    std::vector<char> buf{'y', 'e', 's'}; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-13-16]
    std::printf("%s\n", buf.data());
    return 0;
}
