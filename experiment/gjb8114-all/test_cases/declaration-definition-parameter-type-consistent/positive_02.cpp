void update(const int* data, int& total);

int main()
{
    int value = 5;
    int total = 0;
    update(&value, total);
    return 0;
}

void update(const int* data, int& total)
{
    total = *data;
}
