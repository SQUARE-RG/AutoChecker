int main()
{
    bool a = false;
    bool b = true;
    int result = 0;
    if (!a && b) // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-2-4]
    {
        result = 1;
    }
    else
    {
        result = 2;
    }
    return result;
}
