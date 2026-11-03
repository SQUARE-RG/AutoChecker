#include <cstdlib>

int main()
{
    int* p = static_cast<int*>(std::malloc(sizeof(int)));
    *p = 1; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-3-8]
    std::free(p);
    return 0;
}
