int positive_03(int value)
{
    if (value < 0) {
        throw value;
    }
    return value;
}

int main()
{
    return positive_03(1);
}
