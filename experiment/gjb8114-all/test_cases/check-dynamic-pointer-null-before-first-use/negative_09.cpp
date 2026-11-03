#include <cstdlib>

int main()
{
    int* p = static_cast<int*>(std::malloc(sizeof(int)));
    if (p == nullptr)
    {
        return -1;
    }

    int* q = static_cast<int*>(std::realloc(p, sizeof(int) * 2));
    *q = 42; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-3-8]

    std::free(q);
    return 0;
}
