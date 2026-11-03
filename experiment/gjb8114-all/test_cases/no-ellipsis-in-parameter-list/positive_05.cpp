template <typename T>
T accumulate(T initial, T value)
{
    return initial + value;
}

int main()
{
    return accumulate(1, 2);
}
