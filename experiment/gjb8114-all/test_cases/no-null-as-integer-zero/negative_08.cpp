#include <cstdlib>

int scale(int factor = NULL); // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-13-14]

int main()
{
    int result = scale();
    return result;
}

int scale(int factor)
{
    return factor * 2;
}
