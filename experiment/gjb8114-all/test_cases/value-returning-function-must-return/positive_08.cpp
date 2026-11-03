int count_down(int n)
{
    do
    {
        if (n <= 0)
        {
            return 0;
        }
        --n;
    } while (n > 0);
    return n;
}

int main()
{
    return count_down(3) == 0 ? 0 : 1;
}
