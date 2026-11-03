int main()
{
    int values[3] = {1, 2, 3};
    int index = 1;
    index++;
    values[index] = 10;
    int total = values[0] + values[1];
    index--;
    return total;
}
