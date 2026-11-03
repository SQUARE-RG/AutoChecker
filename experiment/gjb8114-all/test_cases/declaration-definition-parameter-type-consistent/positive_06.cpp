int total(int values[], int count);

int total(int* values, int count)
{
    int sum = 0;
    for (int i = 0; i < count; ++i)
    {
        sum += values[i];
    }
    return sum;
}

int main()
{
    int data[3] = {1, 2, 3};
    return total(data, 3);
}
