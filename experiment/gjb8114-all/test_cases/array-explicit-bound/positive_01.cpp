int main(void)
{
    int array[3] = {0, 1, 2};
    int data = 0;
    for (int i = 0; i < 3; ++i)
    {
        data += array[i];
    }
    return data == 3 ? 0 : 1;
}
