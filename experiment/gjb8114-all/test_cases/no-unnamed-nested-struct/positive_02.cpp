struct Container
{
    struct Item
    {
        int key;
        int value;
    } first, second;
    int count;
};

int main()
{
    Container c{};
    c.first.key = 1;
    c.second.value = 2;
    c.count = 3;
    return 0;
}
