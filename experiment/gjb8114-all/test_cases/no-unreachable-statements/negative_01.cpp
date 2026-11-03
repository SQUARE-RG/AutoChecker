int process(int para)
{
    int local = 0;
    switch (para)
    {
        local = para; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-8-1]
        case 1:
            local = 1;
            break;
        case 2:
            local = 2;
            break;
        default:
            local = -1;
            break;
    }
    return local;
}

int main()
{
    return process(1);
}
