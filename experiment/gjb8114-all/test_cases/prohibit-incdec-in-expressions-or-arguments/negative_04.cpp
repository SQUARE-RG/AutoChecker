int main()
{
    int x = 10;
    int y = 2;
    int result = --x + y; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-6-5]
    return result;
}
