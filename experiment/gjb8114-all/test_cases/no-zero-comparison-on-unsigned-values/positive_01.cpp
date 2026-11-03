#include <cstdint>

int main()
{
    int x = -1;
    int flag = 0;
    if (x >= 0) {
        flag = flag + 1;
    }
    if (x < 0) {
        flag = flag + 1;
    }
    return flag;
}
