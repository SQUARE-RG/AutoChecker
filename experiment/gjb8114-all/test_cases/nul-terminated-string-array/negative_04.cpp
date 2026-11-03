#include <cstdio>

int main()
{
    char letters[3] = {'a', 'b', 'c'}; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-13-16]
    std::puts(letters);
    return 0;
}
