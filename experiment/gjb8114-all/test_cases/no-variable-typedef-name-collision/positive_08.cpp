typedef unsigned int TData;

int main()
{
    unsigned int values[3] = {1u, 2u, 3u};
    unsigned int sum = 0u;
    for (TData value : values)
    {
        sum += value;
    }
    return static_cast<int>(sum);
}
