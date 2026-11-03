int sumArray(int values[], int count);

int main()
{
    int values[3] = {1, 2, 3};
    return sumArray(values, 3) == 6 ? 0 : 1;
}

int sumArray(int values[], int count)
{
    int total = 0;
    for (int i = 0; i < count; ++i)
        total += values[i];
    return total;
}
