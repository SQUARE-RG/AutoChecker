#include <cstddef>

void advance_pointer(int* p, std::ptrdiff_t offset)
{
    p += offset; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-3-3]
    (void)p;
}
