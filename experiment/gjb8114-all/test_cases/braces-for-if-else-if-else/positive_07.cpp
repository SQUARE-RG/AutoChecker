int main()
{
    if constexpr (sizeof(int) == 4)
    {
        return 0;
    }
    else
    {
        return 1;
    }
}
