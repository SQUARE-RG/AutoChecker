#include <cstddef>

int main()
{
    const char *p = NULL;
    try
    {
        throw p;
    }
    catch (const char *)
    {
    }
    catch (int)
    {
    }
    return 0;
}
