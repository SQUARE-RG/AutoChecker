[[nodiscard]] static int compute(int value)
{
    return value * 2;
}

template <typename T>
T use_compute(T value)
{
    return static_cast<T>(compute(static_cast<int>(value)));
}

int main()
{
    return use_compute(5);
}
