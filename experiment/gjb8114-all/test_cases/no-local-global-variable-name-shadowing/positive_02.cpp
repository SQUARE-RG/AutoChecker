int limit = 10;
int main()
{
    int total = 0;
    {
        int count = 2;
        total += count;
    }
    return total + limit;
}
