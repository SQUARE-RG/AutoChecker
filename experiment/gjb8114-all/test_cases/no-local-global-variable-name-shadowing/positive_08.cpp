#include <stdexcept>

int error_code = 0;

int main()
{
    try {
        throw std::runtime_error("boom");
    } catch (const std::runtime_error& ex) {
        (void)ex;
        return error_code + 1;
    }
}
