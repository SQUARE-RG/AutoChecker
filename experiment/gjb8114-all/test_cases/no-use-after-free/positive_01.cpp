#include <cstdlib>

int main()
{
    int* p = static_cast<int*>(std::malloc(sizeof(int)));
    if (p == nullptr) {
        return -1;
    }

    *p = 42;
    int value = *p;
    std::free(p);
    p = nullptr;

    return value == 42 ? 0 : 1;
}
