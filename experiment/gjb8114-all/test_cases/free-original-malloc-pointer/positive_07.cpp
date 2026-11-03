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

    int *original = p;
    char *bytes = reinterpret_cast<char *>(p);
    bytes += sizeof(int);
    *reinterpret_cast<int *>(bytes) = 2;

    free(original);
    return 0;
}
