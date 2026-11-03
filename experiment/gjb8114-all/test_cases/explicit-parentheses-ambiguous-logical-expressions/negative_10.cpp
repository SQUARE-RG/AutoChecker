int main()
{
    bool a = true;
    bool b = false;
    bool c = true;
    bool d = false;
    int result = 0;

    if (a || b && c && d) // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-2-4]
    {
        result = 1;
    }
    else
    {
        result = 0;
    }

    return result;
}
