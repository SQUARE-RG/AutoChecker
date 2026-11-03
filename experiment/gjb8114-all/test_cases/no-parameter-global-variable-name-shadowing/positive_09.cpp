int value = 0;

template <typename T>
T transform(T input)
{
    return input + value;
}

int main()
{
    value = 3;
    int result = transform(4);
    return result;
}
