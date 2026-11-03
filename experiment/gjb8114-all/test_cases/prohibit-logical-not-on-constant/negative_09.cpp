int main()
{
    bool b = !0.0f; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-6-10]
    return b ? 0 : 1;
}
