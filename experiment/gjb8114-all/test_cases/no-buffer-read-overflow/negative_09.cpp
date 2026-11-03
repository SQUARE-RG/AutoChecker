#include <string>

int main()
{
    char src[4] = {'a', 'b', 'c', 'd'};
    std::string s(src, src + 6); // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-6-14]
    return 0;
}
