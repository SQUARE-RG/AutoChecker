// if-else-if chain inside a switch case terminated by a final else branch.
int select(int state, int a, int b)
{
    int v = 0;
    switch (state)
    {
    case 1:
        if (a > 0 && b > 0) { v = 1; } else if (a == 0 || b == 0) { v = 2; } else { v = 3; }
        break;
    default:
        v = -1;
        break;
    }
    return v;
}

int main()
{
    return select(1, 1, 1);
}
