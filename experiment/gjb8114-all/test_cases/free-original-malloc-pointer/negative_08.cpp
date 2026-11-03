#include <cstdlib>
#include <iterator>

using std::malloc;
using std::free;
using std::next;

int main()
{
    int *p = static_cast<int *>(malloc(2 * sizeof(int)));
    if (p == nullptr)
    {
        return 1;
    }

    int *q = next(p);
    *q = 2;

    free(q); // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-6-17]
    return 0;
}
