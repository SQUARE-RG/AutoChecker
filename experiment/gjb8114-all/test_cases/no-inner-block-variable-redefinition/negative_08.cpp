int main()
{
    int err = 0;

    try
    {
        throw 1;
    }
    catch (int)
    {
        int err = 2; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-13-7]
        err += 1;
    }

    return err;
}
