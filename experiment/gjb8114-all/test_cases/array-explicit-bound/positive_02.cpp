int global_array[3] = {10, 20, 30};

int main(void)
{
    int data = 0;
    for (int i = 0; i < 3; ++i)
    {
        data += global_array[i];
    }
    return data == 60 ? 0 : 1;
}
