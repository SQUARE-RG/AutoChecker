int fsub(int *a, int *b)
{
    int sub = 0;
    if ((*a) > (*b))
    {
        sub = (*a) - (*b);
    }
    else if ((*a) < (*b))
    {
        sub = (*b) - (*a);
    }
    else
    {
        sub = 0;
    }
    return sub;
}

int main()
{
    int a = 1;
    int b = 2;
    int sub = fsub(&a, &b);
    return sub;
}
