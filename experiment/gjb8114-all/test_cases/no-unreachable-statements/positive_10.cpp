#include <exception>

void maybe_stop(bool stop)
{
    if (stop)
    {
        std::terminate();
    }
    int after_if = 42;
    (void)after_if;
}
