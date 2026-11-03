typedef unsigned int TData;

int main()
{
    if (TData value = 1u; value > 0u)
    {
        return static_cast<int>(value);
    }
    return 0;
}
