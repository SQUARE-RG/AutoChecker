#include <exception>
#include <iostream>
#include <stdexcept>

void parseNumber(int value) noexcept
{
    try {
        if (value < 0) {
            throw std::invalid_argument("negative value");
        }
        std::cout << "value=" << value << "\n";
    } catch (std::exception const& e) {
        std::cout << "handled: " << e.what() << "\n";
    } catch (...) {
        std::cout << "handled: unknown failure\n";
    }
}

int main()
{
    parseNumber(5);
    parseNumber(-3);
    return 0;
}
