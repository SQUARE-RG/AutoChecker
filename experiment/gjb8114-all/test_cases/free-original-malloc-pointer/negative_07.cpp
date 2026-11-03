#include <cstdlib>

using std::malloc;
using std::free;

int main()
{
    int *p = static_cast<int *>(malloc(3 * sizeof(int)));
    if (p == nullptr)
    {
        return 1;
    }

    char *bytes = reinterpret_cast<char *>(p);
    bytes += sizeof(int);
    *reinterpret_cast<int *>(bytes) = 2;

    free(bytes); // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-6-17]
    return 0;
}
