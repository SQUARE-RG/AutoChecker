int accumulate(int key)
{
    int total = 0;
    switch (key)
    {
        case 1:
            for (int i = 0; i < 4; ++i)
            {
                if (total > 100)
                {
                    break;
                }
                total += i;
            }
            break;
        case 2:
            total += 2;
            break;
        default:
            total = -1;
            break;
    }
    return total;
}

int main()
{
    return accumulate(1);
}
