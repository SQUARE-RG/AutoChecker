int main()
{
    int x = 0;
    int y = 1;
    for (int i = 0; (i < 3) | (x == 0); ++i) { // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-6-4]
        y = y + i;
    }
    return y;
}
