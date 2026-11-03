int main()
{
    unsigned long product = 1;
    for (unsigned long i = 6; i > 0; --i)
    {
        product *= i;
    }
    return static_cast<int>(product);
}
