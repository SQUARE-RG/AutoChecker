#include <cstddef>

int main()
{
    try
    {
        throw static_cast<const char *>(NULL);
    }
    catch (const char *)
    {
    }
    catch (int)
    {
    }
    return 0;
}
