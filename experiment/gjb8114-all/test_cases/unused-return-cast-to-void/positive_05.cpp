#include <functional>

int compute_value(int input)
{
    return input + 1;
}

int main()
{
    (void)std::invoke(compute_value, 41);
    return 0;
}
