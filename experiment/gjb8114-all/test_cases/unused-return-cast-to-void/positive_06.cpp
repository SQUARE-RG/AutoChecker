int main()
{
    int seed = 7;
    (void)([seed]() { return seed + 1; }());
    return 0;
}
