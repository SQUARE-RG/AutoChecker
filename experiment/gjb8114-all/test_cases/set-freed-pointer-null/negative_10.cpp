#include <cstdlib>

int main()
{
    int* p = static_cast<int*>(std::malloc(sizeof(int)));
    if (p == nullptr)
    {
        return 1;
    }
    *p = 42;

    int** pp = &p;
    std::free(*pp); // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-3-6]

    return 0;
}
