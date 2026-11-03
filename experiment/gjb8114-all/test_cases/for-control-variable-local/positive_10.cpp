template <typename T>
int compute(T start)
{
    int result = 0;
    if constexpr (true)
    {
        for (T i = start; i < start + 5; ++i)
        {
            result += static_cast<int>(i);
        }
    }
    return result;
}

int main()
{
    return compute(0);
}
