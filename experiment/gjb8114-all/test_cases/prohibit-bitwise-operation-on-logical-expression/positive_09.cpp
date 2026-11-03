int main()
{
    int x = 0;
    int y = 1;
    for (int i = 0; (i < 3) || (x == 0); ++i) {
        y = y + i;
    }
    return y;
}
