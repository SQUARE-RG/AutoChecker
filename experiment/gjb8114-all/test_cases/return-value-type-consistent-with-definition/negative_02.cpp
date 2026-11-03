int fun(int par)
{
    if (par > 0)
    {
        return 2.5; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-7-10]
    }
    return par;
}

int main()
{
    int result = fun(1);
    return result;
}
