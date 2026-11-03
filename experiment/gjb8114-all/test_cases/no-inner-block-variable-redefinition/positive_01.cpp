int main(void)
{
    int value = 1;
    int result = 0;
    if (value == 1)
    {
        int localValue = 2;
        result = value + localValue;
    }
    return result;
}
