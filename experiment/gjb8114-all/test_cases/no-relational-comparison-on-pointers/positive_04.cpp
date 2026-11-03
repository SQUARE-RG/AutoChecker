int locate(int* values, int count, int* target)
{
    for (int i = 0; i < count; ++i)
    {
        if (&values[i] == target)
        {
            return i;
        }
    }
    return -1;
}
