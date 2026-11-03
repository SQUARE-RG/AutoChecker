#include <cstdlib>

int main()
{
    int data[8] = {0, 0, 0, 0, 0, 0, 0, 0};
    int offset = -5;
    int idx = std::abs(offset);
    data[idx] = 1;
    return 0;
}
