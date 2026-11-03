#include <cstdlib>

int main()
{
    long* data = static_cast<long*>(std::malloc(sizeof(long)));
    if (data == nullptr)
    {
        return 1;
    }

    *data = 42L;

    do
    {
        std::free(data);
        data = nullptr;
    } while (false);

    return 0;
}
