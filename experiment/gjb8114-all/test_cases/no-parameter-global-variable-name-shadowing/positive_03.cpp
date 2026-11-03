int base = 7;

int add_base(int delta)
{
    return delta + base;
}

int main()
{
    auto twice = [](int amount) {
        return amount + base;
    };
    return add_base(1) + twice(2);
}
