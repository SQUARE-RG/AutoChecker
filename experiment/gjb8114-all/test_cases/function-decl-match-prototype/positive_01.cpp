int addTen(int value);

int main()
{
    int amount = 20;
    int result = addTen(amount);
    return result == 30 ? 0 : 1;
}

int addTen(int value)
{
    return value + 10;
}
