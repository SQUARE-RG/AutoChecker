int main()
{
    bool connected = false;
    bool authorized = true;
    int result = 0;

    if (!connected || authorized) { // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-2-4]
        result = 1;
    }

    return result;
}
