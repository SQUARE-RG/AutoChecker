#include <iostream>

static bool accept(bool value)
{
    return value;
}

int main()
{
    unsigned int count = 3u;
    bool result = accept(count >= 2u);
    return result ? 0 : 1;
}
