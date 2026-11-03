int main()
{
    int x = 5;
    int y = -2;
    return ((x > 0) | (y < 0)) ? 0 : 1; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-6-4]
}
