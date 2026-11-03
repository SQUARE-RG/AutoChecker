#include <cstdint>

int count(unsigned int value)
{
    int result = 0;
    constexpr unsigned int threshold = 8;
    if (value == 0) {
        return 0;
    }
    if (value != 0) {
        result = 1;
    }
    if (value >= threshold) {
        result = result + 1;
    }
    return result;
}

int main()
{
    return count(4);
}
