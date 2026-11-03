#include <cstdlib>

enum class Slot : int { kFirst = 0, kSecond = 1 };

int main()
{
    int data[2] = {0, 0};
    data[static_cast<int>(Slot::kSecond)] = 4;
    return EXIT_SUCCESS;
}
