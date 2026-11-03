int main()
{
    int x = 1;
    int z = 0;

    switch (x)
    {
        case 1:
        {
            auto set = [&z](int v) { z = v; };
            set(1);
            break;
        }
        case 2:
        {
            auto get = []() { return 2; };
            z = get();
            break;
        }
        default:
        {
            z = 3;
            break;
        }
    }

    return z;
}
