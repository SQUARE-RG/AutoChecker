int main()
{
    unsigned int remaining = 3u;
    int processed = 0;
    while (remaining >= 1u)
    {
        --remaining;
        ++processed;
    }
    return processed;
}
