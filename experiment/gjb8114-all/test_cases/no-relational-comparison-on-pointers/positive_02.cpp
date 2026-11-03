int main()
{
    int values[2] = {1, 2};
    int *p = &values[0];
    int *q = &values[1];
    int result = 0;

    if (p == q)
    {
        result = 0;
    }
    else if (*p < *q)
    {
        result = *p;
    }
    else
    {
        result = *q;
    }

    return result;
}
