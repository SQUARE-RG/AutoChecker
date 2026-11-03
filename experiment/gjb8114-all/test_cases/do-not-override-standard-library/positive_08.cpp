template <typename T, typename Func>
T apply_twice(T value, Func func)
{
    return func(func(value));
}

int main()
{
    int start = 3;
    int result = apply_twice(start, [](int value) { return value + 2; });
    return result == 7 ? 0 : 1;
}
