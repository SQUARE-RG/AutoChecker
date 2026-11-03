extern int fetchValue(); // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-1-23]

static int datax = 0;

int main(void)
{
    datax = 1;
    return fetchValue();
}

int fetchValue(void)
{
    return datax;
}
