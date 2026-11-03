static int add_one(int value) { return value + 1; }

int main()
{
    int seed = 10;
    auto apply = [seed]() { return add_one(seed); };
    return apply() - 11;
}
