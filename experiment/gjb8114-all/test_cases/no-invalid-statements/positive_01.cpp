static unsigned int transform(unsigned int value)
{
    return value + 1;
}

int main()
{
    unsigned int local = 1;
    unsigned int result = transform(local);
    return static_cast<int>(result);
}
