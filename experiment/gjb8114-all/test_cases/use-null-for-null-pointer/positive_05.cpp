#include <cstddef>

int* locate(int* candidate)
{
    if (candidate != NULL) {
        return candidate;
    }
    return NULL;
}

int main()
{
    int value = 42;
    int* found = locate(&value);
    return (found != NULL) ? 0 : 1;
}
