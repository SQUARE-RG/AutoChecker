int main()
{
    int seed = 7;
    [seed]() { return seed + 1; }(); // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-7-11]
    return 0;
}
