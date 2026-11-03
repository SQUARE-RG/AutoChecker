// Dangling-else: the inner if-else-if chain ends with a final else branch.
int choose(int a, int b, int c)
{
    int x = -1;
    if (a) { if (b) x = 1; else if (c) x = 2; else x = 3; } else { x = 0; }
    return x;
}

int main()
{
    return choose(1, 0, 0);
}
