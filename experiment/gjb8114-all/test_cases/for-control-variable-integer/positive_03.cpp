int main()
{
    unsigned short total = 0;
    for (unsigned short i = 0; i < 10; i += 2)
    {
        total += i;
    }
    return static_cast<int>(total);
}
