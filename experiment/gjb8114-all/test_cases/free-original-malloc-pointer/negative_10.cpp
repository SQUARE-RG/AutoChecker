#include <cstdlib>

int main(int argc, char** argv)
{
    (void)argv;
    int* p = static_cast<int*>(std::malloc((argc + 2) * sizeof(int)));
    if (p == nullptr)
    {
        return -1;
    }

    int offset = argc > 0 ? argc : 1;
    p[0] = 1;
    std::free(p + offset); // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-6-17]
    return 0;
}
