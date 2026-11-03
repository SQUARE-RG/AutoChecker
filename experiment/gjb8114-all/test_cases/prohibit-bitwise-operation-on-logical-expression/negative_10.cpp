bool check(int x, int y)
{
    return (x == 1) & (y == 2); // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-6-4]
}

int main()
{
    return check(1, 2) ? 0 : 1;
}
