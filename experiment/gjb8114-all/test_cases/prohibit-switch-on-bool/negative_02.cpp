int compute(bool flag)
{
    int result = 0;
    switch (flag) // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-4-4]
    {
        case true:
            result = 1;
            break;
        case false:
            result = 2;
            break;
    }
    return result;
}

int main()
{
    return compute(true);
}
