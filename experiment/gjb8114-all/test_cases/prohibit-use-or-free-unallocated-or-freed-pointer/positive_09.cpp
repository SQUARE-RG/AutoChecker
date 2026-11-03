#include <cstdlib>

static int global_storage = 0;

int main()
{
    int* pointer = &global_storage;
    *pointer = 42;
    int read_value = *pointer;
    (void)read_value;
    return 0;
}
