#include <iostream>

static bool accept(bool value)
{
    return value;
}

int main()
{
    unsigned int count = 3u;
    bool result = accept(count >= 0); // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-12-4]
    return result ? 0 : 1;
}
