unsigned int combine(unsigned int a, unsigned int b)
{
    return (unsigned int)(a + b); // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-10-6]
}

int main()
{
    unsigned int x = 1u;
    unsigned int y = 2u;
    return combine(x, y) == 3u ? 0 : 1;
}
