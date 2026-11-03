#define MAKE_DOUBLER(expr) [](int value) { return (expr); }

int main()
{
    auto doubler = MAKE_DOUBLER(value * 2);
    return doubler(3) == 6 ? 0 : 1;
}
