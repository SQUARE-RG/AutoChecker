#include <cstddef>

void do_throw(bool flag)
{
    if (flag)
    {
        throw (NULL); // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-2-8-5]
    }
}

int main()
{
    do_throw(false);
    return 0;
}
