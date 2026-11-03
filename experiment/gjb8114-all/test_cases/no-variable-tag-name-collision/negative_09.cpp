struct Item
{
    int value;
};

int main()
{
    Item items[2] = {{1}, {2}};
    for (struct Item Item : items) // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-13-4]
    {
        (void)Item.value;
    }
    return 0;
}
