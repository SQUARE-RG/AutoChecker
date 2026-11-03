#include <iostream>

int main()
{
    long long large = 9876543210LL;
    int truncated = static_cast<int>(large / 1000LL);
    return truncated == 9876543 ? 0 : 1;
}
