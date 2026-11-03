struct Item
{
    int value;
};

int main()
{
    Item items[2] = {{1}, {2}};
    for (Item item : items)
    {
        (void)item.value;
    }
    return 0;
}
