namespace detail
{
    constexpr int base_value()
    {
        return 7;
    }
}

#define BASE_VALUE detail::base_value

int main()
{
    int v = BASE_VALUE();
    return v;
}
