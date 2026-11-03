#include <cstdio>

struct DivResult {
    bool ok;
    int value;
};

DivResult safe_divide(int a, int b)
{
    if (b == 0) {
        return DivResult{false, 0};
    }
    return DivResult{true, a / b};
}

int main()
{
    DivResult r = safe_divide(10, 0);
    if (!r.ok) {
        std::puts("division failed");
        return 1;
    }
    std::printf("result=%d\n", r.value);
    return 0;
}
