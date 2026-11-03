int item = 42;

int main()
{
    int values[2] = {1, 2};
    for (int element : values) {
        (void)element;
    }
    return item;
}
