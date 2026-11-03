int main()
{
    auto compute = []() {
        int seed = 5;
        seed = seed * 2;
#include <stddef.h> // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-2-3]
        return seed + static_cast<int>(sizeof(size_t));
    };

    return compute();
}
