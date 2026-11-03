int main()
{
    int* values = new int[3]{0, 1, 2};
    int sum = 0;
    for (int i = 0; i < 3; ++i)
    {
        sum += values[i];
    }
    delete[] values;
    return sum;
}
