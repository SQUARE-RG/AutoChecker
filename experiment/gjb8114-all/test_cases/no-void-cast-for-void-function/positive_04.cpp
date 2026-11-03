int main()
{
    auto f = [](int value) {
        if (value < 0) {
            value = -value;
        }
    };
    f(7);
    return 0;
}
