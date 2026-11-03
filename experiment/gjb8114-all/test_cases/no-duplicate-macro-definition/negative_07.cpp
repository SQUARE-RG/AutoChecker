#define SCALE_AREA(x) ((x) * 2)

int compute(void)
{
#define SCALE_AREA(x) ((x) * 3) // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-1-5]
    return SCALE_AREA(5);
}

int main(void)
{
    return compute();
}
