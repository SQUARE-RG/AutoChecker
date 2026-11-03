int main()
{
    int x = 1;
    int y = 0;

    switch (x)
    {
        case 1:
            y = 5;
            [[fallthrough]]; // CHECK-MESSAGES: :[[@LINE]]:13: warning: shared case annotation missing [ucassaat-r-1-4-7]
        case 2:
            y += 7;
            break;
        default:
            y = -1;
            break;
    }

    return y;
}
