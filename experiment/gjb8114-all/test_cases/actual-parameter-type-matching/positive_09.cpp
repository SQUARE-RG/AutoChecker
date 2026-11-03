template <typename T>
T consume(T value)
{
    return value;
}

int main()
{
    long value = 7;
    long result = consume<long>(value);
    return static_cast<int>(result);
}
