#include <cstdlib>

static int global_storage = 0;

int main()
{
    std::free(&global_storage); // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-3-5]
    return 0;
}
