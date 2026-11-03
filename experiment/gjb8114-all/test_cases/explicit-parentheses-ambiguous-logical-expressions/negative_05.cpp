int main()
{
    bool a = true;
    bool b = false;
    bool c = true;
    bool d = false;
    bool result = a && b || c && d; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-2-4]
    return result ? 0 : 1;
}
