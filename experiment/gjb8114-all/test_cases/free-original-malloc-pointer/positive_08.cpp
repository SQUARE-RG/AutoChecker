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

    int *original = p;
    int *q = next(p);
    *q = 2;

    free(original);
    return 0;
}
