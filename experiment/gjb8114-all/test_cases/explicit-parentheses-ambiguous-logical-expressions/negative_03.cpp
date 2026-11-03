int main()
{
    bool a = true;
    bool b = false;
    bool c = true;
    int result = 0;
    if (a || b && c) // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-2-4]
    {
        result = 1;
    }
    else
    {
        result = 2;
    }
    return result;
}
