#include <cstdlib>

unsigned int pfun(unsigned int *pa);

int main()
{
    unsigned int data = 0;
    unsigned int result = pfun(&data);
    return 0;
}

unsigned int pfun(unsigned int *pa)
{
    static unsigned int i = 10;
    pa = &i; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-3-3]
    i = i + 1;
    return i;
}
