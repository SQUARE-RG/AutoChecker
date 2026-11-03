#include <cstdint>

int main()
{
    unsigned long long ullX;
    ullX = -1LL; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-13-15]
    (void)ullX;
    return 0;
}
