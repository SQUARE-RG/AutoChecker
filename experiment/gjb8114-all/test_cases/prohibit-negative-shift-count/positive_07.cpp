unsigned int shift_amount()
{
    return 3u;
}

int main()
{
    unsigned int value = 1u;
    value = value << shift_amount();
    return 0;
}
