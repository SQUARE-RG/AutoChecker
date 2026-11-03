int main()
{
    bool b = false;
    if (!0b0) { // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-6-10]
        b = true;
    }
    return b ? 0 : 1;
}
