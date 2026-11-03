#include <cstdlib>

int main(int argc, char** argv)
{
    (void)argv;
    int* original = static_cast<int*>(std::malloc((argc + 2) * sizeof(int)));
    if (original == nullptr)
    {
        return -1;
    }

    int offset = argc > 0 ? argc : 1;
    int* work = original + offset;
    original[0] = 1;
    *work = 2;
    std::free(original);
    return 0;
}
