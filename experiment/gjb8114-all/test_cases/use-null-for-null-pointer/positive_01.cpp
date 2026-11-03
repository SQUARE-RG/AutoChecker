#include <cstddef>
#include <cstdlib>

int main() {
    int* x = static_cast<int*>(std::malloc(sizeof(int)));
    if (x != NULL)
    {
        *x = 1;
    } else {
        return -1;
    }
    std::free(x);
    return 0;
}
