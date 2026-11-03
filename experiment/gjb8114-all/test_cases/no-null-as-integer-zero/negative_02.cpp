#include <cstddef>

int getWidth()
{
    return NULL; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-13-14]
}

int main()
{
    return getWidth();
}
