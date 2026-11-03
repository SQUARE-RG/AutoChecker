int main()
{
    struct LocalFlags
    {
        signed int flag : 4;
    };

    LocalFlags flags{};
    flags.flag = -1;
    return 0;
}
