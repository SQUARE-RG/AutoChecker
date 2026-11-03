int process(int value)
{
    int result = 0;
    switch (value)
    {
        case 1: // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-4-7]
            result = 1;
            goto finished;
        case 2:
            result = 2;
            break;
        default:
            result = -1;
            break;
    }
finished:
    return result;
}

int main()
{
    return process(1);
}
