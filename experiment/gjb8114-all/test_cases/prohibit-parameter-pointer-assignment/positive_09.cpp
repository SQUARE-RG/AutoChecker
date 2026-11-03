unsigned int sum_array(unsigned int* values, unsigned int count)
{
    unsigned int total = 0;
    for (unsigned int i = 0; i < count; ++i) {
        total += values[i];
    }
    return total;
}

int main()
{
    unsigned int data[3] = {1, 2, 3};
    return sum_array(data, 3) == 6 ? 0 : 1;
}
